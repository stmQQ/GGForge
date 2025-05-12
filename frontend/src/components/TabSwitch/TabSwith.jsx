import "./tabswich.scss";
export default function TabSwich({ tabs, activeTab, onTabClick }) {
    return (
        <div className="tabs">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              className={`tab ${activeTab === tab.id ? "tab--active" : ""}`}
              onClick={() => onTabClick(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>
      );
}