import "./button.scss";

export default function SubmitButton({
  text,
  onClick,
  disabled = false,
  type = "submit",
  isSent = false,
}) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`button button__submit ${isSent ? "sent" : ""}`}
    >
      {text}
    </button>
  );
}
