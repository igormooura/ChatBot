import { Loader } from "lucide-react";

const LoadingIndicator = () => {
  return (
    <div className="flex items-center space-x-3 px-4 py-2 bg-gray-200 rounded-2xl rounded-bl-none shadow-md max-w-[80%] md:max-w-[70%]">
      <Loader className="animate-spin w-6 h-6 text-blue-500" />
      
    </div>
  );
};

export default LoadingIndicator;
