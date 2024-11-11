import React, { useState } from "react";

function AddMessage(messages: any[], newMessage: any): any[] {
  return [...messages, newMessage];
}

export default function ChatInput({ messages, setMessage }: any) {
  const [inputValue, setInputValue] = useState("");

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  };

  const handleSubmit = async () => {
    let messageStruct = {
      text: inputValue,
      dark_color: true,
    };

    let newMessages = AddMessage(messages, messageStruct);

    try {
      const response = await fetch(
        "https://ab31-35-188-180-15.ngrok-free.app/predict_bert",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ input_data: inputValue }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to send message");
      }

      const data = await response.json();

      let responseStruct = {
        text: "Sua intenção é " + data.predicted_labels[0] + "?",
        dark_color: false,
        label_index: 0,
        labels: data.predicted_labels,
        correct_label: false,
      };

      newMessages = [...newMessages, responseStruct];
    } catch (error) {
      console.error("Error:", error);
    }

    setMessage(newMessages);
    setInputValue("");
  };

  return (
    <div className="flex items-center w-72 mx-auto">
      <label className="sr-only">Search</label>
      <div className="relative w-full">
        <input
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white"
          required
        />
      </div>
      <button
        type="button"
        className="py-2.5 px-3 ms-2 text-sm font-medium text-gray-700 rounded-lg border-none bg-slate-400 hover:bg-slate-500"
        onClick={handleSubmit}
      >
        Enviar
      </button>
    </div>
  );
}
