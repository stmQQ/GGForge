import "./button.scss";

export default function ModalButton({ text, onClick, style="" }) {
	return (
		<button onClick={onClick} className={`button button__modal ${style}`}>{text}</button>
	);
}