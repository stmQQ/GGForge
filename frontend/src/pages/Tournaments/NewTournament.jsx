import "./newtournament.scss";

import { useLocation, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";

import TitleH2 from "../../components/TitleH2/TitleH2";
import TextInput from "../../components/InputFields/TextInput";
import SubmitButton from "../../components/Button/SubmitButton";
import RadioGroup from "../../components/InputFields/RadioGroup";
import AvatarUploader from "../../components/CreateTeamForm/AvatarUploader";
import TextareaField from "../../components/InputFields/TextareaField";

export default function NewTournamentPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { game, tournamentName } = location.state || {};
  const [date, setDate] = useState("");
  const [time, setTime] = useState("");
  const [contact, setContact] = useState("");
  const [prizePool, setPrizePool] = useState("");
  const [groupStage, setGroupStage] = useState(false);
  const [slots, setSlots] = useState(4);
  const [selectedSlots, setSelectedSlots] = useState(4);
  const [playoffStage, setPlayoffStage] = useState("single");
  const [matchFormat, setMatchFormat] = useState("bo1");
  const [finalFormat, setFinalFormat] = useState("bo1");
  const [imageFile, setImageFile] = useState(null);
  const [description, setDescription] = useState("");
  // const [imageError, setImageError] = useState(false);
  // const [image, setImage] = useState(null);
  // const [imageError, setImageError] = useState(false);

  useEffect(() => {
    if (!game || !tournamentName) {
      // Если пришли напрямую или потеряли state — редирект обратно
      navigate("/", { replace: true });
    }
  }, [game, tournamentName, navigate]);

  const handleSubmit = (e) => {
    e.preventDefault();
    // if (!image) {
    //   setImageError(true);
    //   return;
    // }
    // setImageError(false);
    // if (!imageFile) {
    //   setImageError(true);
    //   return;
    // }
    // setImageError(false);
    console.log("Форма отправлена!", imageFile);
    console.log("Ура!");
    navigate("/tournaments?tournament=open&organizer=manager");
  };

  return (
    <div className="newtournament">
      <div className="newtournament__header">
        {/* <div className="field-wrapper"> */}
        <AvatarUploader
          onChange={(file) => {
            setImageFile(file);
            // setImageError(false);
          }}
        />
        {/* {imageError && <p className="error-text">Загрузите изображение</p>} */}
        {/* </div> */}
        <div className="newtournament__header-left">
          <p>По игре: {game.title}</p>
          <TitleH2 style="aboutgame__header-title" title={tournamentName} />
        </div>
      </div>
      <form className="newtournament__section" onSubmit={handleSubmit}>
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
          id="tournament-date"
          label="Ваши контакты"
          type="text"
          value={contact}
          onChange={(e) => setContact(e.target.value)}
          placeholder="Как с вами связаться"
        />
        <TextInput
          id="tournament-prize"
          label="Призовой фонд, &#8381;"
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
            { id: "finalFormat-bo2", label: "bo3", value: "bo3" },
            { id: "finalFormat-bo3", label: "bo5", value: "bo5" },
          ]}
        />

        <SubmitButton text="Создать" />
      </form>
    </div>
  );
}
