import { ChatPage } from "@/components/chat/chat-page";

export default function ChatRoute() {
  return (
    // Negate the p-6 padding from (main) layout so chat fills the full area
    <div className="-m-6 h-[calc(100vh_-_var(--header-height,4rem))] flex flex-col overflow-hidden">
      <ChatPage />
    </div>
  );
}
