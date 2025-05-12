import "./button.scss";

export default function ExternalLinkButton({ text, href, disabled = false }) {
  return (
    <a
      href={disabled ? "#" : href}
      className={`button button__external ${disabled ? "disabled" : ""}`}
      target="_blank"
      rel="noopener noreferrer"
      onClick={(e) => disabled && e.preventDefault()}
    >
      {text}
    </a>
  );
}