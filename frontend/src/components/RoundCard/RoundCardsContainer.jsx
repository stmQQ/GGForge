import RoundCard from "./RoundCard";
import "./roundCardContainer.scss";

export default function RoundCardsContainer({ users, isRequest, isTeam = false, onSelect, selectedTeamId, style="" }) {
  return (
    <div className={`round-card-container ${style}`}>
      {users.map((f) => (
        <RoundCard
          key={f.id}
          id={f.id}
          avatar={f.avatar}
          name={f.name}
          isRequest={isRequest}
          isTeam={isTeam}
          onSelect={onSelect}
          selectedTeamId={selectedTeamId}
        />
      ))}
    </div>
  );
}
