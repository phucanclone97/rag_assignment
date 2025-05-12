const BotAvatar = () => {
  return <div className="avatar bot">Bot</div>;
};

const UserAvatar = () => {
  return <div className="avatar user">U</div>;
};

const Avatar = ({ isUser }) => {
  return isUser ? <UserAvatar /> : <BotAvatar />;
};

export default Avatar;
