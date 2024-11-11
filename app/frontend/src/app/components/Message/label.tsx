import IntentButtons from "./intent_buttons";
import React, { useEffect } from "react";

export default function ChatLabel({ messages, setMessage }: any) {
  let _class_left = "w-4/5 mt-1.5 bg-slate-500 px-4 py-2 rounded-lg text-left";
  let _class_right =
    "w-4/5 mt-1.5 bg-slate-600 px-4 py-2 rounded-lg text-right";

  useEffect(() => {
    console.log(messages);
  }, [messages]);

  return (
    <div className="w-full overflow-y-scroll gap-2">
      {messages.map((message: any, index: any) =>
        message.dark_color ? (
          <div key={index.toString()} className="w-full flex justify-end">
            <div key={index.toString()} className={_class_right}>
              {message.text}
            </div>
          </div>
        ) : (
          <div className="w-full overflow-y-scroll gap-2">
            <div key={index.toString()} className={_class_left}>
              {message.text}
            </div>
            {!message.correct_label && (
              <IntentButtons
                messages={messages}
                setMessage={setMessage}
                index={index}
              ></IntentButtons>
            )}
          </div>
        )
      )}
    </div>
  );
}
