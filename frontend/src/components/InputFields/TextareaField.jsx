import "./inputFields.scss";

export default function TextareaField({
  id,
  label,
  value,
  onChange,
  placeholder,
}) {
  return (
    <div className="field-wrapper">
      <label className="field-label" htmlFor={id}>
        {label}
      </label>
      <textarea
        id={id}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className="textarea-input"
      />
    </div>
  );
}
