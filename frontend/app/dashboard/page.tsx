"use client";

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-gray-950 text-white p-8">
      <h1 className="text-3xl font-bold mb-8">Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Usage Card */}
        <div className="bg-gray-900 p-6 rounded-xl border border-gray-800">
          <h3 className="text-xl font-semibold mb-4 text-blue-400">Usage</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Daily Requests</span>
                <span>12 / 50</span>
              </div>
              <div className="w-full bg-gray-800 rounded-full h-2">
                <div className="bg-blue-500 h-2 rounded-full" style={{ width: '24%' }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Storage</span>
                <span>45 MB / 1 GB</span>
              </div>
              <div className="w-full bg-gray-800 rounded-full h-2">
                <div className="bg-green-500 h-2 rounded-full" style={{ width: '4%' }}></div>
              </div>
            </div>
          </div>
        </div>

        {/* Subscription Card */}
        <div className="bg-gray-900 p-6 rounded-xl border border-gray-800">
          <h3 className="text-xl font-semibold mb-4 text-purple-400">Subscription</h3>
          <p className="text-2xl font-bold mb-2">Pro Plan</p>
          <p className="text-gray-400 text-sm mb-4">Active until May 25, 2024</p>
          <button className="w-full py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors border border-gray-700">
            Manage Subscription
          </button>
        </div>

        {/* System Status */}
        <div className="bg-gray-900 p-6 rounded-xl border border-gray-800">
          <h3 className="text-xl font-semibold mb-4 text-green-400">System Status</h3>
          <ul className="space-y-2 text-sm">
            <li className="flex items-center space-x-2">
              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
              <span>Backend API: Operational</span>
            </li>
            <li className="flex items-center space-x-2">
              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
              <span>Vector DB: Operational</span>
            </li>
            <li className="flex items-center space-x-2">
              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
              <span>Graph DB: Operational</span>
            </li>
             <li className="flex items-center space-x-2">
              <span className="w-2 h-2 bg-yellow-500 rounded-full"></span>
              <span>Desktop Client: Disconnected</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
