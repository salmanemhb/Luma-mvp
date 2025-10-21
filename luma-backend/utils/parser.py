"""
Parser utilities - extract structured data from text, CSV, and Excel
Optimized for Spanish utility bills and ERP exports
"""

import re
import csv
import logging
from datetime import datetime
from typing import List, Dict, Optional
from decimal import Decimal

logger = logging.getLogger(__name__)

# Spanish month names
SPANISH_MONTHS = {
    'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
    'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
    'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
}

# Column name synonyms (ES/EN)
COLUMN_SYNONYMS = {
    'date': ['date', 'fecha', 'date_invoice', 'invoice_date', 'fecha_factura'],
    'supplier': ['supplier', 'proveedor', 'vendor', 'empresa', 'company'],
    'category': ['category', 'categoria', 'tipo', 'type', 'concept', 'concepto'],
    'usage': ['usage', 'consumo', 'consumption', 'quantity', 'cantidad', 'amount'],
    'unit': ['unit', 'unidad', 'units', 'uom'],
    'cost': ['cost', 'coste', 'importe', 'total', 'amount', 'precio', 'price'],
    'invoice_number': ['invoice', 'invoice_number', 'factura', 'numero_factura', 'n_factura'],
    'notes': ['notes', 'observaciones', 'comments', 'comentarios', 'description']
}


def parse_csv(file_path: str) -> List[Dict]:
    """
    Parse CSV file with flexible column mapping
    Supports both ES and EN column names
    """
    try:
        records = []
        
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            # Detect delimiter
            sample = f.read(1024)
            f.seek(0)
            delimiter = ',' if ',' in sample else ';'
            
            reader = csv.DictReader(f, delimiter=delimiter)
            
            # Map columns
            column_map = _map_columns(reader.fieldnames)
            
            for row in reader:
                record = _extract_record_from_row(row, column_map)
                if record:
                    records.append(record)
        
        logger.info(f"✅ Parsed CSV: {len(records)} records")
        return records
        
    except Exception as e:
        logger.error(f"❌ CSV parsing failed: {str(e)}")
        return []


def parse_xlsx(file_path: str) -> List[Dict]:
    """
    Parse Excel file (.xlsx)
    """
    try:
        import openpyxl
        
        workbook = openpyxl.load_workbook(file_path, data_only=True)
        sheet = workbook.active
        
        records = []
        
        # Get headers (first row)
        headers = [cell.value for cell in sheet[1]]
        column_map = _map_columns(headers)
        
        # Parse data rows
        for row in sheet.iter_rows(min_row=2, values_only=True):
            row_dict = {headers[i]: row[i] for i in range(len(headers)) if i < len(row)}
            record = _extract_record_from_row(row_dict, column_map)
            if record:
                records.append(record)
        
        logger.info(f"✅ Parsed Excel: {len(records)} records")
        return records
        
    except ImportError:
        logger.error("❌ openpyxl not installed. Run: pip install openpyxl")
        return []
    except Exception as e:
        logger.error(f"❌ Excel parsing failed: {str(e)}")
        return []


def parse_text(text: str) -> List[Dict]:
    """
    Parse unstructured text (from OCR)
    Extracts utility bill data using Spanish regex patterns
    
    Targets: Endesa, Iberdrola, Naturgy, Repsol invoices
    """
    try:
        records = []
        
        # Extract supplier
        supplier = _extract_supplier(text)
        
        # Extract invoice number
        invoice_number = _extract_invoice_number(text)
        
        # Extract date
        date = _extract_date(text)
        
        # Extract electricity consumption (kWh)
        kwh_data = _extract_kwh(text)
        if kwh_data:
            records.append({
                'supplier': supplier or 'Unknown',
                'category': 'electricity',
                'usage': kwh_data['usage'],
                'unit': 'kWh',
                'cost': kwh_data.get('cost'),
                'date': date,
                'invoice_number': invoice_number
            })
        
        # Extract gas consumption (m³)
        gas_data = _extract_gas(text)
        if gas_data:
            records.append({
                'supplier': supplier or 'Unknown',
                'category': 'natural_gas',
                'usage': gas_data['usage'],
                'unit': 'm3',
                'cost': gas_data.get('cost'),
                'date': date,
                'invoice_number': invoice_number
            })
        
        # Extract fuel (diesel/petrol)
        fuel_data = _extract_fuel(text)
        if fuel_data:
            records.append({
                'supplier': supplier or 'Unknown',
                'category': fuel_data['type'],
                'usage': fuel_data['usage'],
                'unit': 'L',
                'cost': fuel_data.get('cost'),
                'date': date,
                'invoice_number': invoice_number
            })
        
        logger.info(f"✅ Parsed text: {len(records)} records extracted")
        return records
        
    except Exception as e:
        logger.error(f"❌ Text parsing failed: {str(e)}")
        return []


def _map_columns(headers: List[str]) -> Dict[str, str]:
    """
    Map CSV/Excel columns to standardized names
    """
    column_map = {}
    
    for standard_name, synonyms in COLUMN_SYNONYMS.items():
        for header in headers:
            if header and header.lower().strip() in synonyms:
                column_map[header] = standard_name
                break
    
    return column_map


def _extract_record_from_row(row: Dict, column_map: Dict) -> Optional[Dict]:
    """
    Extract standardized record from CSV/Excel row
    """
    try:
        record = {}
        
        for original_col, standard_col in column_map.items():
            value = row.get(original_col)
            
            if value is not None and value != '':
                if standard_col in ['usage', 'cost']:
                    # Parse numeric values (handle comma decimals)
                    record[standard_col] = _parse_number(value)
                elif standard_col == 'date':
                    record[standard_col] = _parse_date_value(value)
                else:
                    record[standard_col] = str(value).strip()
        
        # Infer category from supplier/unit if missing
        if 'category' not in record and 'supplier' in record and 'unit' in record:
            record['category'] = _infer_category(record['supplier'], record['unit'])
        
        # Must have at least usage or cost
        if 'usage' in record or 'cost' in record:
            return record
        
        return None
        
    except Exception as e:
        logger.debug(f"Row parsing error: {str(e)}")
        return None


def _parse_number(value) -> Optional[float]:
    """Parse number with comma/dot decimal handling"""
    try:
        if isinstance(value, (int, float)):
            return float(value)
        
        # Handle Spanish format: 1.234,56 -> 1234.56
        value_str = str(value).strip()
        value_str = value_str.replace('.', '').replace(',', '.')
        value_str = re.sub(r'[^\d.-]', '', value_str)  # Remove currency symbols
        
        return float(value_str) if value_str else None
    except:
        return None


def _parse_date_value(value) -> Optional[datetime]:
    """Parse date from various formats"""
    if isinstance(value, datetime):
        return value.date()
    
    try:
        date_str = str(value).strip()
        
        # Try common formats
        for fmt in ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%d.%m.%Y']:
            try:
                return datetime.strptime(date_str, fmt).date()
            except:
                continue
        
        return None
    except:
        return None


def _infer_category(supplier: str, unit: str) -> str:
    """Infer emission category from supplier and unit"""
    supplier_lower = supplier.lower()
    unit_lower = unit.lower()
    
    if 'kwh' in unit_lower or any(s in supplier_lower for s in ['endesa', 'iberdrola', 'naturgy', 'eléctrica']):
        return 'electricity'
    elif 'm3' in unit_lower or 'm³' in unit_lower or 'gas' in supplier_lower:
        return 'natural_gas'
    elif 'l' == unit_lower or 'litro' in unit_lower:
        if 'diesel' in supplier_lower or 'gasóleo' in supplier_lower:
            return 'diesel'
        else:
            return 'petrol'
    elif 'tonne' in unit_lower or 'ton' in unit_lower or 'km' in unit_lower:
        return 'freight_transport'
    else:
        return 'purchased_goods'


# Spanish utility bill regex patterns

def _extract_supplier(text: str) -> Optional[str]:
    """Extract supplier name"""
    suppliers = ['Endesa', 'Iberdrola', 'Naturgy', 'Repsol', 'Cepsa', 'Gas Natural']
    for supplier in suppliers:
        if supplier.lower() in text.lower():
            return supplier
    return None


def _extract_invoice_number(text: str) -> Optional[str]:
    """Extract invoice/bill number"""
    patterns = [
        r'N[úu]mero\s+(?:de\s+)?factura[:\s]+([A-Z0-9-]+)',
        r'Factura\s+n[úu]m\.\s*([A-Z0-9-]+)',
        r'Invoice\s+(?:number|#)[:\s]+([A-Z0-9-]+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def _extract_date(text: str) -> Optional[datetime]:
    """Extract date from text"""
    # Pattern: DD/MM/YYYY or DD-MM-YYYY
    pattern = r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})'
    matches = re.findall(pattern, text)
    if matches:
        day, month, year = matches[0]
        try:
            return datetime(int(year), int(month), int(day)).date()
        except:
            pass
    return None


def _extract_kwh(text: str) -> Optional[Dict]:
    """Extract electricity consumption (kWh)"""
    patterns = [
        r'Consumo[:\s]+([0-9.,]+)\s*kWh',
        r'([0-9.,]+)\s*kWh',
        r'Energía consumida[:\s]+([0-9.,]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            usage = _parse_number(match.group(1))
            if usage and usage > 0:
                # Try to find associated cost
                cost = _extract_cost_near(text, match.start())
                return {'usage': usage, 'cost': cost}
    return None


def _extract_gas(text: str) -> Optional[Dict]:
    """Extract gas consumption (m³)"""
    patterns = [
        r'Consumo[:\s]+([0-9.,]+)\s*m[³3]',
        r'([0-9.,]+)\s*m[³3]',
        r'Gas natural[:\s]+([0-9.,]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            usage = _parse_number(match.group(1))
            if usage and usage > 0:
                cost = _extract_cost_near(text, match.start())
                return {'usage': usage, 'cost': cost}
    return None


def _extract_fuel(text: str) -> Optional[Dict]:
    """Extract fuel consumption (Liters)"""
    patterns = [
        r'(Diesel|Gasóleo|Gasolina)[:\s]+([0-9.,]+)\s*[Ll]',
        r'([0-9.,]+)\s*[Ll]itros?\s+(?:de\s+)?(Diesel|Gasóleo|Gasolina)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            fuel_type = 'diesel' if 'diesel' in match.group(0).lower() or 'gasóleo' in match.group(0).lower() else 'petrol'
            usage = _parse_number(match.group(2) if len(match.groups()) > 1 else match.group(1))
            if usage and usage > 0:
                cost = _extract_cost_near(text, match.start())
                return {'type': fuel_type, 'usage': usage, 'cost': cost}
    return None


def _extract_cost_near(text: str, position: int, window: int = 200) -> Optional[float]:
    """Extract cost near a given position in text"""
    # Look within +/- window characters
    start = max(0, position - window)
    end = min(len(text), position + window)
    snippet = text[start:end]
    
    # Pattern for EUR amounts
    patterns = [
        r'([0-9.,]+)\s*€',
        r'€\s*([0-9.,]+)',
        r'Total[:\s]+([0-9.,]+)',
        r'Importe[:\s]+([0-9.,]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, snippet, re.IGNORECASE)
        if match:
            cost = _parse_number(match.group(1))
            if cost and cost > 0:
                return cost
    
    return None
