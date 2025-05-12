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
              <p className="message-text">{message.text}</p>
              <p className="message-reasoning">{message.reasoning}</p>
              <p className="message-fit-tips">{message.fitTips}</p>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Message;
