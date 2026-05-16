import React from 'react';
import { Upload, ArrowRight, GitCommit } from 'lucide-react';

export default function VersionCompare() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-white">Version Compare</h1>
      
      <div className="flex items-center gap-4">
        <div className="flex-1 bg-[#2D2D2D] border border-dashed border-[#333333] rounded-lg p-8 flex flex-col items-center justify-center cursor-pointer hover:border-[#0078D4] transition-colors shadow-sm group">
          <Upload className="text-gray-400 group-hover:text-[#0078D4] mb-2 transition-colors" />
          <p className="text-sm font-medium text-white">Upload Old ADMX Snapshot</p>
          <p className="text-xs text-gray-500">output_v1.json</p>
        </div>
        <ArrowRight className="text-[#333333]" size={32} />
        <div className="flex-1 bg-[#2D2D2D] border border-dashed border-[#0078D4] rounded-lg p-8 flex flex-col items-center justify-center cursor-pointer hover:bg-[#111111] transition-colors shadow-sm group">
          <Upload className="text-[#0078D4] mb-2" />
          <p className="text-sm font-medium text-[#0078D4]">Upload New ADMX Snapshot</p>
          <p className="text-xs text-gray-500">output_v2.json (Ready)</p>
        </div>
      </div>

      <div className="bg-[#2D2D2D] rounded-lg border border-[#333333] overflow-hidden shadow-lg">
        <div className="p-4 border-b border-[#333333] bg-[#111111] flex justify-between items-center">
          <h2 className="font-medium text-white flex items-center gap-2">
            <GitCommit size={18} className="text-purple-500"/> Diff Results
          </h2>
          <span className="text-xs bg-purple-500/20 text-purple-400 px-2 py-1 rounded border border-purple-500/30">4 Changes Detected</span>
        </div>
        <div className="p-4 space-y-4">
          <div className="p-4 bg-green-500/5 border border-green-500/20 rounded-md shadow-sm">
            <h3 className="text-green-400 font-medium text-sm flex items-center gap-2">+ Added (1)</h3>
            <p className="text-sm mt-2 text-gray-300">ApprovedActiveXInstallSites_V2</p>
          </div>
          <div className="p-4 bg-red-500/5 border border-red-500/20 rounded-md shadow-sm">
            <h3 className="text-red-400 font-medium text-sm flex items-center gap-2">- Removed (1)</h3>
            <p className="text-sm mt-2 text-gray-300">DisableAccountNotifications</p>
          </div>
          <div className="p-4 bg-yellow-500/5 border border-yellow-500/20 rounded-md shadow-sm">
            <h3 className="text-yellow-400 font-medium text-sm flex items-center gap-2">~ Modified (2)</h3>
            <div className="mt-2 space-y-3">
              <div>
                <p className="text-sm font-medium text-white">AxISURLZonePolicies</p>
                <div className="text-xs font-mono mt-1 grid grid-cols-2 gap-4">
                  <div className="bg-red-500/10 border border-red-500/20 p-2 rounded text-red-200">Before: This policy setting controls...</div>
                  <div className="bg-green-500/10 border border-green-500/20 p-2 rounded text-green-200">After: [Updated in v2] This policy setting...</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
