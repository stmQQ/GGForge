import "./newtournament.scss";
import { useLocation, useNavigate } from "react-router-dom";
import { useState, useEffect, useContext } from "react";
import { AuthContext } from "../../context/AuthContext";
import { createTournament } from "../../api/tournaments";
import TitleH2 from "../../components/TitleH2/TitleH2";
import TextInput from "../../components/InputFields/TextInput";
import SubmitButton from "../../components/Button/SubmitButton";
import RadioGroup from "../../components/InputFields/RadioGroup";
import TextareaField from "../../components/InputFields/TextareaField";
import AvatarUploader from "../../components/CreateTeamForm/AvatarUploader";

export default function NewTournamentPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { isAuthenticated } = useContext(AuthContext);
  const { game, tournamentName } = location.state || {};
  const [date, setDate] = useState("");
  const [time, setTime] = useState("");
  const [contact, setContact] = useState("");
  const [prizePool, setPrizePool] = useState("");
  const [groupStage, setGroupStage] = useState(false);
  const [slots, setSlots] = useState(4);
  const [selectedSlots, setSelectedSlots] = useState(4);
  const [matchFormat, setMatchFormat] = useState("bo1");
  const [finalFormat, setFinalFormat] = useState("bo1");
  const [description, setDescription] = useState("");
  const [imageFile, setImageFile] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/login", { replace: true });
    }
    if (!game || !tournamentName) {
      navigate("/", { replace: true });
    }
  }, [isAuthenticated, game, tournamentName, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!date || !time) {
      setError("Укажите дату и время");
      return;
    }
    const localDateTime = new Date(`${date}T${time}`);
    const startTime = localDateTime.toISOString();

    if (startTime < new Date()) {
      setError("Дата и время должны быть в будущем");
      return;
    }
    if (prizePool && !/^\d+(\.\d{3})*$/.test(prizePool.replace(/\s/g, ""))) {
      setError("Некорректный формат призового фонда");
      return;
    }
    if (
      contact &&
      !/^([^\s@]+@[^\s@]+\.[^\s@]+|@[\w\d_]{5,32}|https?:\/\/(t\.me|vk\.com)\/[\w\d_]{3,32}|vk\.com\/[\w\d_]{3,32})$/.test(contact.trim())
    ) {
      setError("Некорректный формат контакта (email, ссылка на Telegram или VK)");
      return;
    }


    const maxParticipants = groupStage ? selectedSlots : slots;
    const numGroups = groupStage ? (maxParticipants <= 16 ? 2 : 4) : undefined;
    const maxParticipantsPerGroup = groupStage ? Math.ceil(maxParticipants / numGroups) : undefined;
    const playoffParticipantsCountPerGroup = groupStage
      ? (() => {
        const maxRows = maxParticipantsPerGroup;
        if (maxRows <= 4) return Math.ceil(maxRows / 2);
        if (maxRows === 5) return 2;
        if (maxRows >= 6 && maxRows <= 8) return 4;
        return maxRows - 2;
      })()
      : undefined;

    const tournamentData = new FormData();
    const jsonData = {
      title: tournamentName,
      game_id: game.id,
      start_time: startTime,
      format_: matchFormat,
      final_format_: finalFormat,
      max_participants: maxParticipants,
      prize_fund: prizePool ? parseInt(prizePool.replace(/[\s.]/g, "")) : undefined,
      contact: contact,
      description: description,
      has_group_stage: groupStage,
      has_playoff: true,
      num_groups: numGroups,
      max_participants_per_group: maxParticipantsPerGroup,
      playoff_participants_count_per_group: playoffParticipantsCountPerGroup,
    };
    Object.entries(jsonData).forEach(([key, value]) => {
      if (value !== undefined) tournamentData.append(key, value);
    });
    if (imageFile) tournamentData.append("img", imageFile);


    try {
      const response = await createTournament(tournamentData);
      setError("");
      navigate(`/tournament/${response.data.tournament.id}`);
    } catch (err) {
      setError(err.response?.data?.msg || "Ошибка создания турнира");
    }
  };

  return (
    <div className="newtournament">
      <div className="newtournament__header">
        <AvatarUploader
          onChange={(file) => {
            setImageFile(file);
            setError("");
          }}
        />
        <div className="newtournament__header-left">
          <p>По игре: {game?.title}</p>
          <TitleH2 style="aboutgame__header-title" title={tournamentName} />
        </div>
      </div>
      <form className="newtournament__section" onSubmit={handleSubmit}>
        {error && <div className="error-message">{error}</div>}
        <TextInput
          id="tournament-date"
          label="Дата проведения"
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
        />
        <TextInput
          id="tournament-time"
          label="Время начала"
          type="time"
          value={time}
          onChange={(e) => setTime(e.target.value)}
        />
        <TextInput
          id="tournament-contacts"
          label="Ваши контакты"
          type="text"
          value={contact}
          onChange={(e) => setContact(e.target.value)}
          placeholder="Email или телефон"
        />
        <TextInput
          id="tournament-prize"
          label="Призовой фонд, ₽"
          type="text"
          value={prizePool}
          onChange={(e) => setPrizePool(e.target.value)}
          placeholder="Введите сумму"
        />
        <TextareaField
          id="tournament-description"
          label="Описание турнира:"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Введите описание"
        />

        <div className="newtournament__checkbox">
          <input
            type="checkbox"
            id="groupStage"
            checked={groupStage}
            onChange={(e) => setGroupStage(e.target.checked)}
          />
          <label className="field-label" htmlFor="groupStage">
            Групповой этап
          </label>
        </div>

        {!groupStage ? (
          <>
            <div className="newtournament__amount-radio">
              <label className="field-label">Количество участников</label>
              <div className="radio-group">
                {[4, 8, 16, 32].map((value) => (
                  <label key={value} className="radio-option">
                    <input
                      type="radio"
                      name="slots"
                      value={value}
                      checked={slots === value}
                      onChange={() => setSlots(value)}
                    />
                    {value}
                  </label>
                ))}
              </div>
            </div>
            <RadioGroup
              label="Формат матчей"
              name="matchFormat"
              value={matchFormat}
              onChange={setMatchFormat}
              options={[
                { id: "matchFormat-bo1", label: "bo1", value: "bo1" },
                { id: "matchFormat-bo3", label: "bo3", value: "bo3" },
              ]}
            />
          </>
        ) : (
          <div className="field-wrapper">
            <label className="field-label" htmlFor="group-stage-slider">
              Количество участников
            </label>
            <input
              type="range"
              id="group-stage-slider"
              min={4}
              max={32}
              step={2}
              value={selectedSlots}
              onChange={(e) => setSelectedSlots(Number(e.target.value))}
            />
            <div className="range-value">{selectedSlots}</div>
            <RadioGroup
              label="Формат матчей"
              name="matchFormat"
              value={matchFormat}
              onChange={setMatchFormat}
              options={[
                { id: "matchFormat-bo1", label: "bo1", value: "bo1" },
                { id: "matchFormat-bo2", label: "bo2", value: "bo2" },
                { id: "matchFormat-bo3", label: "bo3", value: "bo3" },
              ]}
            />
          </div>
        )}

        <RadioGroup
          label="Формат финала"
          name="finalFormat"
          value={finalFormat}
          onChange={setFinalFormat}
          options={[
            { id: "finalFormat-bo1", label: "bo1", value: "bo1" },
            { id: "finalFormat-bo3", label: "bo3", value: "bo3" },
            { id: "finalFormat-bo5", label: "bo5", value: "bo5" },
          ]}
        />

        <SubmitButton text="Создать" />
      </form>
    </div>
  );
}