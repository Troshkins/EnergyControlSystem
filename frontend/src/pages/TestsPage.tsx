// src/pages/TestsPage.tsx
import { mockData } from '../data/mockData';

export default function TestsPage() {
  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Test Scenarios Results</h1>

      <div className="bg-zinc-900 rounded-3xl overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-zinc-800">
              <th className="text-left py-5 px-8 font-medium">Scenario</th>
              <th className="text-left py-5 px-8 font-medium">Description</th>
              <th className="text-center py-5 px-8 font-medium">Status</th>
              <th className="text-right py-5 px-8 font-medium">Total Cost (€)</th>
            </tr>
          </thead>
          <tbody>
            {mockData.testResults.map((test) => (
              <tr key={test.id} className="border-b border-zinc-800 last:border-0 hover:bg-zinc-800/50">
                <td className="py-5 px-8 font-medium">{test.name}</td>
                <td className="py-5 px-8 text-zinc-400">{test.description}</td>
                <td className="text-center">
                  <span className={`inline-block px-4 py-1 rounded-full text-xs font-medium ${
                    test.status === 'passed' 
                      ? 'bg-emerald-900 text-emerald-400' 
                      : 'bg-red-900 text-red-400'
                  }`}>
                    {test.status.toUpperCase()}
                  </span>
                </td>
                <td className="py-5 px-8 text-right font-mono font-semibold">
                  {test.cost.toLocaleString('ru-RU')}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
