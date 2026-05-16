import { useRef, useState } from 'react';
import { Upload, ArrowRight, GitCommit, FileJson } from 'lucide-react';

export default function VersionCompare() {
  const oldFileInputRef = useRef(null);
  const newFileInputRef = useRef(null);

  const [oldFile, setOldFile] = useState(null);
  const [newFile, setNewFile] = useState(null);

  const handleFileChange = (setter) => (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setter(e.target.files[0]);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-white">Version Compare</h1>
      
      <div className="flex items-center gap-4">
        {/* Old File Upload */}
        <div
          onClick={() => oldFileInputRef.current?.click()}
          className={`flex-1 bg-[#2D2D2D] border border-dashed ${oldFile ? 'border-[#0078D4]' : 'border-[#333333]'} rounded-lg p-8 flex flex-col items-center justify-center cursor-pointer hover:border-[#0078D4] hover:bg-[#1a1a1a] transition-colors shadow-sm group`}
        >
          <input
            type="file"
            ref={oldFileInputRef}
            onChange={handleFileChange(setOldFile)}
            accept=".json"
            className="hidden"
          />
          {oldFile ? (
            <>
              <FileJson className="text-[#0078D4] mb-2 transition-colors" />
              <p className="text-sm font-medium text-[#0078D4]">Old Snapshot Selected</p>
              <p className="text-xs text-gray-400 mt-1">{oldFile.name}</p>
            </>
          ) : (
            <>
              <Upload className="text-gray-400 group-hover:text-[#0078D4] mb-2 transition-colors" />
              <p className="text-sm font-medium text-white">Upload Old ADMX Snapshot</p>
              <p className="text-xs text-gray-500 mt-1">Select a JSON file</p>
            </>
          )}
        </div>

        <ArrowRight className="text-[#333333]" size={32} />

        {/* New File Upload */}
        <div
          onClick={() => newFileInputRef.current?.click()}
          className={`flex-1 bg-[#2D2D2D] border border-dashed ${newFile ? 'border-[#0078D4]' : 'border-[#333333]'} rounded-lg p-8 flex flex-col items-center justify-center cursor-pointer hover:border-[#0078D4] hover:bg-[#1a1a1a] transition-colors shadow-sm group`}
        >
          <input
            type="file"
            ref={newFileInputRef}
            onChange={handleFileChange(setNewFile)}
            accept=".json"
            className="hidden"
          />
          {newFile ? (
            <>
              <FileJson className="text-[#0078D4] mb-2 transition-colors" />
              <p className="text-sm font-medium text-[#0078D4]">New Snapshot Selected</p>
              <p className="text-xs text-gray-400 mt-1">{newFile.name}</p>
            </>
          ) : (
            <>
              <Upload className="text-gray-400 group-hover:text-[#0078D4] mb-2 transition-colors" />
              <p className="text-sm font-medium text-white">Upload New ADMX Snapshot</p>
              <p className="text-xs text-gray-500 mt-1">Select a JSON file</p>
            </>
          )}
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
