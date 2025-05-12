const BotAvatar = () => {
  return <div className="avatar bot"></div>;
};

const UserAvatar = () => {
  return <div className="avatar user"></div>;
};

const Avatar = ({ isUser }) => {
  return isUser ? <UserAvatar /> : <BotAvatar />;
};

export default Avatar;
