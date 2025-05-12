import { useRef, useState } from "react";
import "./avatarUploader.scss";

export default function AvatarUploader({ onChange }) {
  const fileInputRef = useRef(null);
  const [previewUrl, setPreviewUrl] = useState(null);

  const handleClick = () => {
    fileInputRef.current.click();
  };

  const handleChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const imageUrl = URL.createObjectURL(file);
      setPreviewUrl(imageUrl);
      onChange(file); // передаём выбранный файл наружу
    }
  };

  return (
    <div className="avatar-uploader" onClick={handleClick}>
      {previewUrl ? (
        <img  src={previewUrl} alt="avatar preview" className="avatar-image" />
      ) : (
        <div className="avatar-placeholder">+</div>
      )}
      <input  
        type="file"
        accept="image/*"
        ref={fileInputRef}
        onChange={handleChange}
        style={{ display: "none" }}
      />
    </div>
  );
}
