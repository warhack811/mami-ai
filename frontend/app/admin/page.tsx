"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import { Save, Lock, Unlock, Database } from 'lucide-react';

interface Setting {
  key: string;
  value: string;
  description: string;
}

export default function AdminPage() {
  const [settings, setSettings] = useState<Setting[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const res = await api.get('/admin/');
      setSettings(res.data);
    } catch (err) {
      console.error("Failed to fetch settings", err);
      // router.push('/login'); // Redirect if not auth
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async (key: string, value: string) => {
    try {
      await api.post('/admin/', { key, value });
      // Show success toast ideally
      alert(`Updated ${key}`);
      fetchSettings();
    } catch (err) {
      alert("Failed to update setting");
    }
  };

  if (loading) return <div className="p-8 text-white">Loading Admin Panel...</div>;

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8 flex items-center">
          <Database className="mr-3 text-blue-500" />
          System Administration
        </h1>

        <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
          <div className="p-4 bg-gray-750 border-b border-gray-700 font-semibold grid grid-cols-12 gap-4">
            <div className="col-span-4">Config Key</div>
            <div className="col-span-6">Value</div>
            <div className="col-span-2">Action</div>
          </div>

          <div className="divide-y divide-gray-700">
            {settings.map((setting) => (
              <SettingRow key={setting.key} setting={setting} onUpdate={handleUpdate} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function SettingRow({ setting, onUpdate }: { setting: Setting, onUpdate: (k: string, v: string) => void }) {
  const [val, setVal] = useState(setting.value);
  const [isEditing, setIsEditing] = useState(false);

  return (
    <div className="p-4 grid grid-cols-12 gap-4 items-center hover:bg-gray-750 transition-colors">
      <div className="col-span-4">
        <div className="font-mono text-sm text-blue-300">{setting.key}</div>
        <div className="text-xs text-gray-400 mt-1">{setting.description}</div>
      </div>
      <div className="col-span-6">
        {isEditing ? (
          <input
            type="text"
            value={val}
            onChange={(e) => setVal(e.target.value)}
            className="w-full bg-gray-900 border border-gray-600 rounded px-2 py-1 text-sm font-mono text-white focus:ring-1 focus:ring-blue-500 outline-none"
          />
        ) : (
          <div className="font-mono text-sm text-gray-300 truncate" title={val}>
            {val}
          </div>
        )}
      </div>
      <div className="col-span-2 flex justify-end">
        {isEditing ? (
          <button
            onClick={() => { onUpdate(setting.key, val); setIsEditing(false); }}
            className="p-2 bg-green-600 hover:bg-green-500 rounded text-white mr-2"
          >
            <Save size={16} />
          </button>
        ) : (
          <button
            onClick={() => setIsEditing(true)}
            className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-xs font-medium"
          >
            Edit
          </button>
        )}
      </div>
    </div>
  );
}
