import './index.scss';
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { useState, useContext } from 'react';
import { AuthContext } from './context/AuthContext';
import Sidebar from './components/Sidebar/Sidebar';
import Header from './components/Header/Header.jsx';
import Home from './pages/Home/Home';
import Games from './pages/Games/Games';
import Friends from './pages/Friends/Friends.jsx';
import Teams from './pages/Teams/Teams.jsx'; // Переименовано с Commands
import AboutGame from './pages/Games/AboutGame.jsx';
import Tournaments from './pages/Tournaments/UserTournaments.jsx';
import NewTournament from './pages/Tournaments/NewTournament.jsx';
import TeamPage from './pages/Teams/TeamPage.jsx';
import TournamentPage from './pages/Tournaments/TournamentPage.jsx';
import Profile from './pages/Profiles/Profile.jsx';
import MyProfile from './pages/Profiles/MyProfile.jsx';
// import Support from './pages/Support/Support.jsx'; // Новый компонент для поддержки

// Компонент для защиты маршрутов
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useContext(AuthContext);
  if (isLoading) return <div>Загрузка...</div>;
  if (!isAuthenticated) {
    // Диспатчим событие unauthorized для открытия модала
    window.dispatchEvent(new CustomEvent('unauthorized'));
    return <Navigate to="/" replace />;
  }
  return children;
};

function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const toggleSidebar = () => {
    setIsSidebarOpen((prev) => !prev);
  };

  return (
    <div className="App">
      <Sidebar isOpen={isSidebarOpen} onClose={toggleSidebar} />
      <Header onMenuToggle={toggleSidebar} />
      <div className="MainWrapper">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/games" element={<Games />} />
          <Route path="/games/:id" element={<AboutGame />} />
          <Route
            path="/friends"
            element={
              <ProtectedRoute>
                <Friends />
              </ProtectedRoute>
            }
          />
          <Route
            path="/teams"
            element={
              <ProtectedRoute>
                <Teams />
              </ProtectedRoute>
            }
          />
          <Route
            path="/tournaments"
            element={
              <Tournaments />
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <MyProfile />
              </ProtectedRoute>
            }
          />
          <Route
            path="/profile/:id"
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            }
          />
          <Route
            path="/newtournament"
            element={
              <ProtectedRoute>
                <NewTournament />
              </ProtectedRoute>
            }
          />
          <Route
            path="/team/:id"
            element={
              <ProtectedRoute>
                <TeamPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/tournament/:id"
            element={
              <ProtectedRoute>
                <TournamentPage />
              </ProtectedRoute>
            }
          />
          {/* <Route
            path="/support"
            element={
              <ProtectedRoute>
                <Support />
              </ProtectedRoute>
            }
          /> */}
        </Routes>
      </div>
    </div>
  );
}

export default App;