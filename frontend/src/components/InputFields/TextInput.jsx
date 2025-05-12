import "./inputFields.scss";

export default function TextInput({ id, label, value, onChange, placeholder, type = "text", name="", disabled = false, style  }) {
  return (
    <div className="field-wrapper">
      <label className="field-label" htmlFor={id}>
        {label}
      </label>
      <input required 
        // type="text"
        type={type}
        id={id}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className="text-input"
        name={name}
        disabled={disabled}
        style={style}
      />
    </div>
  );
}
