import "./titleh2.scss";

export default function TitleH2({title, style=""}) {
  return <h2 className={`title-h2 ${style}`}>{title}</h2>;
}
