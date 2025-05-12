import "./footer.scss";

export default function Footer() {
  return (
    <div className="footer">
      <div className="footer__message">
        Появились вопросы? Пиши нам на почту: <br />{" "}
        <a href="mailto:ggforgesupport@xmail.com" className="footer__link">
          ggforgesupport@xmail.com
        </a>
      </div>
      <div className="footer__authors">Сайт разработан: Burdinova, stmQQ</div>
    </div>
  );
}
