import "./search.scss";
import SearchImg from "../../icons/search.svg?react";

export default function Search({
  placeholder = "",
  value,
  onChange,
  style = "",
}) {
  return (
    <div className="search-wrapper">
      <form className="search" action="" onSubmit={(e) => e.preventDefault()}>
        <input
          className={`search__input ${style}`}
          type="search"
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
        />
        <button className="search__button" type="button">
          <SearchImg className={`search__svg ${style}`} />
        </button>
      </form>
    </div>
  );
}
