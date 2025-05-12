import "./card.scss";
import LinkButton from "../Button/LinkButton";

export default function Card({ reverse,  text, link, linkText, image }) {
	return (
		<div className="card" style={{ flexDirection: reverse ? 'row-reverse' : 'row' }}>
			<div className="card__left" style={{ textAlign: reverse ? 'right' : 'left' }}>
				<p className="card__text">{text}</p>
				<div className="card__button" style={{ alignSelf: reverse ? 'flex-end' : 'flex-start' }}>
				<LinkButton to={link} text={linkText} />
				</div>
				
			</div>
			<div className="card__right">
				<img src={image} alt="" />
			</div>
		</div>
	);
}