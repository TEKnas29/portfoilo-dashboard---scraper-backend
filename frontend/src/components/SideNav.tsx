import React from "react";
import {
  Home as HomeIcon,
  LayoutDashboard,
  FlaskConical,
  Archive,
  User,
  UserPlus,
  Gift,
  ChevronDown,
} from "lucide-react";

type NavItemProps = {
  icon: React.ReactNode;
  text: string;
  pageName: string;
  onClick?: () => void;
  currentPage: string;
};

const NavItem: React.FC<NavItemProps> = ({
  icon,
  text,
  pageName,
  onClick,
  currentPage,
}) => (
  <button
    onClick={onClick}
    className={`
      w-full flex items-center gap-3 px-4 py-2 rounded-lg text-sm transition-colors duration-200
      ${
        currentPage === pageName
          ? "bg-teal-50 text-teal-700 font-medium"
          : "text-gray-700 hover:bg-gray-100 hover:text-gray-900"
      }
    `}
  >
    <span className="flex-shrink-0">{icon}</span>
    <span className="truncate">{text}</span>
  </button>
);

const UserAccount: React.FC = () => {
  return (
    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg mt-auto">
      <div className="flex items-center gap-2">
        <div className="bg-teal-600 text-white rounded-full w-9 h-9 flex items-center justify-center text-sm font-semibold">
          RN
        </div>
        <ChevronDown size={18} className="text-gray-500" />
      </div>
      <div className="text-right">
        <p className="text-gray-800 font-medium text-xs">CMP1Y</p>
        <p className="text-gray-500 text-[11px]">Valid till Apr 19, 2025</p>
      </div>
    </div>
  );
};


type SideNavProps = {
  currentPage: string;
  setCurrentPage: React.Dispatch<React.SetStateAction<string>>;
};
const items = [
  { icon: <HomeIcon size={20} />, text: "Home", pageName: "home" },
  {
    icon: <LayoutDashboard size={20} />,
    text: "Portfolios",
    pageName: "portfolios",
  },
  {
    icon: <FlaskConical size={20} />,
    text: "Experimentals",
    pageName: "experimentals",
  },
  { icon: <Archive size={20} />, text: "Slack Archives", pageName: "archives" },
  {
    icon: <UserPlus size={20} />,
    text: "Refer a friend",
    pageName: "invite-user",
  },
  { icon: <Gift size={20} />, text: "Gift a subscription", pageName: "gift" },
  { icon: <User size={20} />, text: "Account", pageName: "account" },
];

const SideNav: React.FC<SideNavProps> = ({ currentPage, setCurrentPage }) => {
  return (
    <aside
      className="
        fixed z-40 top-0 left-0 w-60 bg-white border-r border-gray-200 
        transition-transform duration-300 ease-in-out
        flex-shrink-0 flex flex-col
        md:translate-x-0 md:static md:shadow-none
      "
    >
      <div className="flex flex-col h-full p-5">
        {/* Header */}
        <div className="flex items-center gap-1">
          <span className="bg-teal-600 text-white px-2 py-0.5 rounded-full text-xs font-semibold">
            capitalmind
          </span>
          <span className="text-teal-600 text-[11px] font-medium">premium</span>
        </div>

        {/* Navigation */}
        <nav className="mt-6 flex-grow flex flex-col gap-1">
          {items.map((item) => (
            <NavItem
              key={item.pageName}
              icon={item.icon}
              text={item.text}
              pageName={item.pageName}
              onClick={() => setCurrentPage(item.pageName)}
              currentPage={currentPage}
            />
          ))}
        </nav>

        {/* User section */}
        <UserAccount />
      </div>
    </aside>
  );
};


export default SideNav;
