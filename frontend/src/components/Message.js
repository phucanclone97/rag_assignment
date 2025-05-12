import Avatar from "./Avatar";

const Message = ({ message, isUser }) => {
  return (
    <div className={`message ${isUser ? "user" : "bot"}`}>
      <div className="message-content">
        <Avatar isUser={isUser} />
        {isUser ? (
          <div>{message.text}</div>
        ) : (
          <div>
            <div>{message.text}</div>
            <div>{message.reasoning}</div>
            <div>{message.fitTips}</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Message;
