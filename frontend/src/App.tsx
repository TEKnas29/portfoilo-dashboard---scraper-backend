import { useState } from "react";
import Home from "./components/Home";
import PortfolioPage from "./components/PortfolioPage";
import SideNav from "./components/SideNav";

function App() {
  const [currentPage, setCurrentPage] = useState("home");

  return (
    <div className="h-screen flex bg-gray-50 font-sans">
      {/* Sidebar (fixed width) */}
      <SideNav currentPage={currentPage} setCurrentPage={setCurrentPage} />

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto ml-60">
        <div className="py-6 px-4 sm:px-6 lg:px-8">
          {currentPage === "portfolios" ? <PortfolioPage /> : <Home />}
        </div>
      </main>
    </div>
  );
}

export default App;
