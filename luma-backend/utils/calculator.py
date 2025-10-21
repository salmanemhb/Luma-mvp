"""
Calculator utilities - emission calculations using factors
"""

import logging
from typing import Dict, Optional
from sqlalchemy.orm import Session
from models.emission_factor import EmissionFactor

logger = logging.getLogger(__name__)


def calculate_emissions(data: Dict, db: Session) -> Optional[Dict]:
    """
    Calculate CO2e emissions for a data record
    
    Args:
        data: Dict with keys: category, usage, unit, supplier
        db: Database session
    
    Returns:
        Dict with: category, scope, co2e, emission_factor, factor_source
    """
    try:
        category = data.get('category')
        usage = data.get('usage')
        unit = data.get('unit')
        supplier = data.get('supplier', '')
        
        if not usage or not unit:
            logger.warning("Missing usage or unit in data")
            return None
        
        # Normalize category and unit
        category = _normalize_category(category, unit, supplier)
        unit = _normalize_unit(unit)
        
        if not category:
            logger.warning(f"Could not determine category for unit {unit}")
            return None
        
        # Get emission factor from database
        factor_record = db.query(EmissionFactor).filter(
            EmissionFactor.category == category,
            EmissionFactor.unit == unit
        ).order_by(EmissionFactor.year.desc()).first()
        
        if not factor_record:
            logger.warning(f"No emission factor found for {category} ({unit})")
            return None
        
        # Calculate emissions (factor is in kgCO2e, convert to tonnes)
        co2e_kg = float(usage) * float(factor_record.factor)
        co2e_tonnes = co2e_kg / 1000.0
        
        # Determine scope
        scope = _determine_scope(category)
        
        return {
            'category': category,
            'scope': scope,
            'co2e': round(co2e_tonnes, 3),
            'emission_factor': float(factor_record.factor),
            'factor_source': f"{factor_record.source} {factor_record.year}"
        }
        
    except Exception as e:
        logger.error(f"Emission calculation failed: {str(e)}")
        return None


def _normalize_category(category: Optional[str], unit: str, supplier: str) -> Optional[str]:
    """
    Normalize category name to match emission_factors table
    """
    if not category:
        # Infer from unit and supplier
        return _infer_category(unit, supplier)
    
    category_lower = category.lower().strip()
    
    # Mapping variations to standard names
    category_map = {
        'electricidad': 'electricity',
        'electric': 'electricity',
        'energia': 'electricity',
        'luz': 'electricity',
        'gas': 'natural_gas',
        'gas_natural': 'natural_gas',
        'gasnatural': 'natural_gas',
        'gasoleo': 'diesel',
        'gasóleo': 'diesel',
        'gasoil': 'diesel',
        'gasolina': 'petrol',
        'petrol': 'petrol',
        'transporte': 'freight_transport',
        'flete': 'freight_transport',
        'compras': 'purchased_goods',
        'materiales': 'purchased_goods',
    }
    
    # Try direct match first
    if category_lower in ['electricity', 'natural_gas', 'diesel', 'petrol', 'freight_transport', 'purchased_goods']:
        return category_lower
    
    # Try mapping
    return category_map.get(category_lower)


def _infer_category(unit: str, supplier: str) -> Optional[str]:
    """
    Infer category from unit and supplier
    """
    unit_lower = unit.lower().strip()
    supplier_lower = supplier.lower()
    
    # Electricity indicators
    if unit_lower in ['kwh', 'mwh']:
        return 'electricity'
    
    if any(s in supplier_lower for s in ['endesa', 'iberdrola', 'naturgy', 'eléctrica', 'electric']):
        return 'electricity'
    
    # Gas indicators
    if unit_lower in ['m3', 'm³']:
        return 'natural_gas'
    
    if 'gas' in supplier_lower:
        return 'natural_gas'
    
    # Fuel indicators
    if unit_lower in ['l', 'litro', 'liter', 'litros', 'liters']:
        if any(s in supplier_lower for s in ['diesel', 'gasóleo', 'gasoil']):
            return 'diesel'
        return 'petrol'
    
    # Transport indicators
    if 'km' in unit_lower or 'tonne' in unit_lower:
        return 'freight_transport'
    
    # Currency = purchased goods
    if unit_lower in ['eur', 'euro', '€', 'usd', 'dollar']:
        return 'purchased_goods'
    
    return None


def _normalize_unit(unit: str) -> str:
    """
    Normalize unit to match emission_factors table
    """
    unit_lower = unit.lower().strip()
    
    unit_map = {
        'kwh': 'kWh',
        'mwh': 'MWh',
        'm3': 'm3',
        'm³': 'm3',
        'l': 'L',
        'litro': 'L',
        'litros': 'L',
        'liter': 'L',
        'liters': 'L',
        'tonne_km': 'tonne_km',
        'eur': 'EUR',
        'euro': 'EUR',
        '€': 'EUR',
    }
    
    return unit_map.get(unit_lower, unit)


def _determine_scope(category: str) -> int:
    """
    Determine GHG Protocol scope (1, 2, or 3)
    
    Scope 1: Direct emissions (owned/controlled sources)
    Scope 2: Indirect emissions from purchased energy
    Scope 3: Other indirect emissions (supply chain)
    """
    scope_map = {
        'natural_gas': 1,  # Combustion on-site
        'diesel': 1,       # Company vehicles
        'petrol': 1,       # Company vehicles
        'electricity': 2,  # Purchased electricity
        'freight_transport': 3,  # Logistics
        'purchased_goods': 3,    # Supply chain
    }
    
    return scope_map.get(category, 3)  # Default to Scope 3


# Testing utilities
if __name__ == "__main__":
    # Test data
    test_cases = [
        {'category': 'electricity', 'usage': 1000, 'unit': 'kWh', 'supplier': 'Endesa'},
        {'category': None, 'usage': 500, 'unit': 'm3', 'supplier': 'Gas Natural'},
        {'category': 'diesel', 'usage': 200, 'unit': 'L', 'supplier': 'Repsol'},
    ]
    
    print("🧮 Testing emission calculator...")
    for test in test_cases:
        print(f"\nInput: {test}")
        category = _normalize_category(test.get('category'), test['unit'], test['supplier'])
        unit = _normalize_unit(test['unit'])
        scope = _determine_scope(category) if category else None
        print(f"  → Category: {category}, Unit: {unit}, Scope: {scope}")
