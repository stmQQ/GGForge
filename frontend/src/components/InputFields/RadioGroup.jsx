import "./inputFields.scss"

// components/InputFields/RadioGroup.js
export default function RadioGroup({ label, name, options, value, onChange }) {
  return (
    <div className="field-wrapper ">
      <p className="field-label">{label}</p>
      {options.map(({ id, label, value: val }) => (
        <div className="radio-option" key={id}>
          <input
            type="radio"
            id={id}
            name={name}
            value={val}
            checked={value === val}
            onChange={(e) => onChange(e.target.value)}
          />
          <label htmlFor={id}>{label}</label>
        </div>
      ))}
    </div>
  );
}
