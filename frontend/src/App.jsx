import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import PolicySearch from './pages/PolicySearch';
import AIAssistant from './pages/AIAssistant';
import ScriptGenerator from './pages/ScriptGenerator';
import RegistryExplorer from './pages/RegistryExplorer';
import VersionCompare from './pages/VersionCompare';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="search" element={<PolicySearch />} />
          <Route path="registry" element={<RegistryExplorer />} />
          <Route path="assistant" element={<AIAssistant />} />
          <Route path="compare" element={<VersionCompare />} />
          <Route path="scripts" element={<ScriptGenerator />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
