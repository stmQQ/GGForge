import { useState } from "react";
import "./CreateTeamForm.scss";
import AvatarUploader from "./AvatarUploader";
import TextInput from "../InputFields/TextInput";
import TextareaField from "../InputFields/TextareaField";
import SubmitButton from "../Button/SubmitButton";
import TitleH2 from "../TitleH2/TitleH2";

export default function CreateTeamForm({ onSubmit }) {
  const [teamName, setTeamName] = useState("");
  const [description, setDescription] = useState("");
  const [logoFile, setLogoFile] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!teamName.trim()) return; // Простая валидация
    onSubmit({ teamName, description, logoFile });
    setTeamName("");
    setDescription("");
    setLogoFile(null);
  };

  return (
    <form className="create-team-form" onSubmit={handleSubmit}>
      <TitleH2 title="Создание команды" />
      <AvatarUploader onChange={(file) => setLogoFile(file)} />

      <TextInput
        id="teamName"
        label="Название команды:"
        value={teamName}
        onChange={(e) => setTeamName(e.target.value)}
        placeholder="Введите название"
        required
      />

      <TextareaField
        id="description"
        label="Описание команды:"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="Введите описание"
      />

      <SubmitButton text="Создать" />
    </form>
  );
}