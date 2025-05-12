import Avatar from "./Avatar";

const Message = ({ message, isUser }) => {
  return (
    <div className={`message ${isUser ? "user" : "bot"}`}>
      <div className="message-content">
        {isUser ? (
          <>
            <div>{message.text}</div>
            <Avatar isUser={isUser} />
          </>
        ) : (
          <>
            <Avatar isUser={isUser} />
            <div>
              <p className="message-text">
                <strong>Recommended Size:</strong>{" "}
                {message.text.replace("Recommended Size: ", "")}
              </p>
              {message.reasoning && (
                <p className="message-reasoning">
                  <strong>Reasoning:</strong> {message.reasoning}
                </p>
              )}
              {message.fitTips && (
                <p className="message-fit-tips">
                  <strong>Fit Tips:</strong> {message.fitTips}
                </p>
              )}
              {console.log(message.sisterSizes)}
              {/* Display Sister Sizes if they exist and the array is not empty */}
              {message.sisterSizes && message.sisterSizes.length > 0 && (
                <p className="message-sister-sizes">
                  <strong>Sister Sizes:</strong>{" "}
                  {message.sisterSizes.join(", ")}
                </p>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Message;
