import PropTypes from "prop-types";
import "./button.scss";
import { Link } from "react-router-dom";

export default function LinkButton(props) {
	return (
		<div>
			<Link to={props.to} className="button button__link">{props.text}</Link>
		</div>
	);
}

LinkButton.propTypes = {
	to: PropTypes.string.isRequired, // Ожидаем, что to — строка и обязательный параметр
	text: PropTypes.string.isRequired, // Ожидаем, что text — строка и обязательный параметр
};