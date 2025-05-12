import "./gameAccount.scss";

export default function GameAccount({
  id,
  title,
  nickname,
  image,
  onDelete,
  showDelete = true,
}) {
  return (
    <div className="gameAccount">
      <div className="gameAccount__title">{title}</div>
      <div className="gameAccount__flex">
        <div className="gameAccount__left">
          <img src={image} alt="" className="gameAccount__image" />
          <div className="gameAccount__nickname">{nickname}</div>
        </div>
        {showDelete && (
          <button className="gameAccount__delete" onClick={() => onDelete(id)}>
            ✖
          </button>
        )}
      </div>
    </div>
  );
}
