import React, { useState } from "react";

export default function IntentButtons({ messages, setMessage, index }: any) {
  const handleLastIntent = async () => {
    const updatedMessages = [...messages];

    if (updatedMessages[index].label_index > 0) {
      updatedMessages[index].text =
        "Sua intenção é " +
        updatedMessages[index].labels[updatedMessages[index].label_index - 1] +
        "?";
      updatedMessages[index].label_index =
        updatedMessages[index].label_index - 1;

      setMessage(updatedMessages);
    }
  };

  const handleNextIntent = async () => {
    const updatedMessages = [...messages];

    if (updatedMessages[index].label_index < 4) {
      updatedMessages[index].text =
        "Sua intenção é " +
        updatedMessages[index].labels[updatedMessages[index].label_index + 1] +
        "?";
      updatedMessages[index].label_index =
        updatedMessages[index].label_index + 1;

      setMessage(updatedMessages);
    }
  };

  const handleSubmit = async () => {
    const updatedMessages = [...messages];
    updatedMessages[index].correct_label = true;
    setMessage(updatedMessages);

    let newMessages = messages;

    try {
      const response = await fetch(
        "https://ab31-35-188-180-15.ngrok-free.app/generate_prompt",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            input_data: updatedMessages[index - 1].text,
            intention:
              updatedMessages[index].labels[updatedMessages[index].label_index],
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to send message");
      }

      const data = await response.json();

      let responseStruct = {
        text: data.result,
        dark_color: false,
        correct_label: true,
      };

      newMessages = [...newMessages, responseStruct];
    } catch (error) {
      console.error("Error:", error);
    }

    setMessage(newMessages);
  };

  return (
    <div>
      <div className="w-4/5 flex items-center content-center justify-center ustify-items-center mt-1 bg-slate-700 rounded-lg">
        <button
          type="button"
          className="py-2 px-4 ms-1 text-sm font-medium text-gray-700 rounded-lg border-none bg-slate-400 hover:bg-slate-500"
          onClick={handleLastIntent}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.5"
            stroke="currentColor"
            className="size-4"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18"
            />
          </svg>
        </button>
        <button
          type="button"
          className="py-2 px-4 ms-1 text-sm font-medium text-gray-700 rounded-lg border-none bg-slate-400 hover:bg-slate-500"
          onClick={handleSubmit}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.5"
            stroke="currentColor"
            className="size-4"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="m4.5 12.75 6 6 9-13.5"
            />
          </svg>
        </button>
        <button
          type="button"
          className="py-2 px-4 ms-1 text-sm font-medium text-gray-700 rounded-lg border-none bg-slate-400 hover:bg-slate-500"
          onClick={handleNextIntent}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.5"
            stroke="currentColor"
            className="size-4"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3"
            />
          </svg>
        </button>
      </div>
      <div className="w-4/5 text-center text-sm">
        {messages[index].label_index + 1}/5
      </div>
    </div>
  );
}
