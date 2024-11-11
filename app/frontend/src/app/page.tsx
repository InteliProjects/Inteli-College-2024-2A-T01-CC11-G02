import "@/app/globals.css";
import ChatBox from "./components/Message/chat";

export default function Home() {
  return (
    <div className="grid items-end min-h-screen min-v-screen sm:p-4">
      <main className="flex items-end h-max">
        <ChatBox />
      </main>
    </div>
  );
}
