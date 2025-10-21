import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, UserPlus, Trash2, Eye, Filter } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { adminAPI } from '@/lib/api';
import { useLanguage } from '@/contexts/LanguageContext';

interface WaitlistSubmission {
  id: number;
  name: string;
  company: string;
  email: string;
  role: string;
  created_at: string;
}

const AdminWaitlist = () => {
  const [submissions, setSubmissions] = useState<WaitlistSubmission[]>([]);
  const [filteredSubmissions, setFilteredSubmissions] = useState<WaitlistSubmission[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState<string>('all');
  const [stats, setStats] = useState({ total: 0, last_24h: 0, last_7d: 0 });
  
  const { toast } = useToast();
  const { t } = useLanguage();
  const navigate = useNavigate();

  useEffect(() => {
    fetchWaitlist();
    fetchStats();
  }, []);

  useEffect(() => {
    filterSubmissions();
  }, [searchTerm, roleFilter, submissions]);

  const fetchWaitlist = async () => {
    try {
      const data = await adminAPI.getWaitlistSubmissions();
      setSubmissions(data.items || []);
      setFilteredSubmissions(data.items || []);
    } catch (error) {
      toast({
        title: t('admin.error'),
        description: 'Failed to load waitlist submissions',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const data = await adminAPI.getWaitlistStats();
      setStats({
        total: data.total_signups || 0,
        last_24h: data.last_24h || 0,
        last_7d: data.last_7d || 0
      });
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const filterSubmissions = () => {
    let filtered = submissions;

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(sub =>
        sub.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        sub.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
        sub.email.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Role filter
    if (roleFilter && roleFilter !== 'all') {
      filtered = filtered.filter(sub => sub.role === roleFilter);
    }

    setFilteredSubmissions(filtered);
  };

  const handlePromote = async (id: number) => {
    if (!confirm('Promote this user to a full company account?')) return;

    try {
      const result = await adminAPI.promoteWaitlistUser(id);
      toast({
        title: 'Success!',
        description: `Created company account. Temp password: ${result.temporary_password}`,
      });
      fetchWaitlist(); // Refresh list
    } catch (error: any) {
      toast({
        title: 'Promotion failed',
        description: error.message || 'Failed to promote user',
        variant: 'destructive'
      });
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this waitlist submission?')) return;

    try {
      await adminAPI.deleteWaitlistSubmission(id);
      toast({
        title: 'Deleted',
        description: 'Waitlist submission removed',
      });
      fetchWaitlist();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to delete submission',
        variant: 'destructive'
      });
    }
  };

  const getRoleBadgeColor = (role: string) => {
    const colors: Record<string, string> = {
      sme: 'bg-blue-100 text-blue-700',
      consultant: 'bg-purple-100 text-purple-700',
      corporate: 'bg-green-100 text-green-700',
      other: 'bg-gray-100 text-gray-700'
    };
    return colors[role] || colors.other;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sage-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Waitlist Management</h1>
        <p className="text-gray-600 mt-1">
          Manage beta signups from the landing page
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Total Signups</CardDescription>
            <CardTitle className="text-3xl">{stats.total}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Last 24 Hours</CardDescription>
            <CardTitle className="text-3xl">{stats.last_24h}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Last 7 Days</CardDescription>
            <CardTitle className="text-3xl">{stats.last_7d}</CardTitle>
          </CardHeader>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search by name, company, or email..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="w-full md:w-48">
              <Select value={roleFilter} onValueChange={setRoleFilter}>
                <SelectTrigger>
                  <Filter className="h-4 w-4 mr-2" />
                  <SelectValue placeholder="Filter by role" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Roles</SelectItem>
                  <SelectItem value="sme">SME</SelectItem>
                  <SelectItem value="consultant">Consultant</SelectItem>
                  <SelectItem value="corporate">Corporate</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Submissions Table */}
      <Card>
        <CardHeader>
          <CardTitle>
            Submissions ({filteredSubmissions.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b text-left">
                  <th className="pb-3 font-semibold">Name</th>
                  <th className="pb-3 font-semibold">Company</th>
                  <th className="pb-3 font-semibold">Email</th>
                  <th className="pb-3 font-semibold">Role</th>
                  <th className="pb-3 font-semibold">Date</th>
                  <th className="pb-3 font-semibold">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredSubmissions.map((sub) => (
                  <tr key={sub.id} className="border-b hover:bg-gray-50">
                    <td className="py-4">{sub.name}</td>
                    <td className="py-4">{sub.company}</td>
                    <td className="py-4 text-sm text-gray-600">{sub.email}</td>
                    <td className="py-4">
                      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getRoleBadgeColor(sub.role)}`}>
                        {sub.role}
                      </span>
                    </td>
                    <td className="py-4 text-sm text-gray-600">
                      {new Date(sub.created_at).toLocaleDateString()}
                    </td>
                    <td className="py-4">
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => navigate(`/admin/waitlist/${sub.id}`)}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="default"
                          className="bg-sage-600 hover:bg-sage-700"
                          onClick={() => handlePromote(sub.id)}
                        >
                          <UserPlus className="h-4 w-4 mr-1" />
                          Promote
                        </Button>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => handleDelete(sub.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {filteredSubmissions.length === 0 && (
              <div className="text-center py-12 text-gray-500">
                No submissions found
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminWaitlist;
