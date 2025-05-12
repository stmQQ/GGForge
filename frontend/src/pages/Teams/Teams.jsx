import "./commands.scss";
import { useState } from "react";

import { commands, requests_commands } from "../../helpers/commands.js";

import TitleH2 from "../../components/TitleH2/TitleH2.jsx";
import TabSwich from "../../components/TabSwitch/TabSwith.jsx";
import ModalButton from "../../components/Button/ModalButton.jsx";
import Modal from "../../components/Modal/Modal.jsx";
import RoundCards from "../../components/RoundCard/RoundCardsContainer.jsx";
import CreateTeamForm from "../../components/CreateTeamForm/CreateTeamForm.jsx";
// import TitleButton from "../../components/TitleH2/TitleButton.jsx";

export default function Commands() {
  const [activeTab, setActiveTab] = useState("commands");
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleCreateTeam = ({ teamName, description, logoFile }) => {
    console.log("Создана команда:");
    console.log("Название:", teamName);
    console.log("Описание:", description);
    console.log("Логотип:", logoFile);

    // тут можешь добавить отправку данных на сервер
    // например: await fetch(...) или axios.post(...)

    setIsModalOpen(false); // закрываем модалку после создания
  };

  const tabs = [
    { id: "commands", label: "Ваши команды" },
    { id: "requests_commands", label: "Приглашения в команды" },
  ];

  return (
    <div>
      <div className="title-with-button">
        <TitleH2 title="Команды" style="indent"/>
        <ModalButton
          text="Создать команду"
          onClick={() => setIsModalOpen(true)}
        />
      </div>

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)}>
        <CreateTeamForm onSubmit={handleCreateTeam} />
      </Modal>

      <TabSwich tabs={tabs} activeTab={activeTab} onTabClick={setActiveTab} />

      <div className="tab-content">
        {activeTab === "commands" ? (
          <RoundCards users={commands} isRequest={false} isTeam={true}/>
        ) : (
          <RoundCards users={requests_commands} isRequest={true} isTeam={true}/>
        )}
      </div>
    </div>
  );
}
