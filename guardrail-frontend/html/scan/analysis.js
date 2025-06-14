const Analysis = () => {
  const [checks, setChecks] = React.useState([
    { id: 1, text: "Scanning endpoint configuration...", done: false },
    { id: 2, text: "Analyzing authentication methods...", done: false },
    { id: 3, text: "Testing input validation...", done: false },
    {
      id: 4,
      text: "Checking prompt injection vulnerabilities...",
      done: false,
    },
    { id: 5, text: "Validating rate limiting...", done: false },
    { id: 6, text: "Examining response handling...", done: false },
  ]);

  const [report, setReport] = React.useState(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    let currentCheck = 0;
    const interval = setInterval(() => {
      if (currentCheck < checks.length) {
        setChecks((prevChecks) =>
          prevChecks.map((check, index) =>
            index === currentCheck ? { ...check, done: true } : check
          )
        );
        currentCheck++;
      } else {
        clearInterval(interval);
        setLoading(false);
        setReport({
          status: "warning",
          findings: [
            "⚠️ Your API accepts Base64-override commands",
            "⚠️ No rate limiting detected on endpoint",
            "⚠️ Weak input validation for prompt parameters",
            "✅ Authentication mechanism properly implemented",
            "✅ Response sanitization in place",
          ],
        });
      }
    }, 1500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <div className="bg-white shadow-lg rounded-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">
            Security Analysis in Progress
          </h2>

          {loading ? (
            <div className="space-y-6">
              {checks.map((check) => (
                <div key={check.id} className="flex items-center space-x-3">
                  <div
                    className={`flex-shrink-0 h-6 w-6 ${
                      check.done ? "text-green-500" : "text-gray-300"
                    }`}
                  >
                    {check.done ? (
                      <svg
                        className="h-6 w-6"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fillRule="evenodd"
                          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                          clipRule="evenodd"
                        />
                      </svg>
                    ) : (
                      <svg
                        className="animate-spin h-6 w-6"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                      >
                        <circle
                          className="opacity-25"
                          cx="12"
                          cy="12"
                          r="10"
                          stroke="currentColor"
                          strokeWidth="4"
                        ></circle>
                        <path
                          className="opacity-75"
                          fill="currentColor"
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        ></path>
                      </svg>
                    )}
                  </div>
                  <span
                    className={`text-lg ${
                      check.done ? "text-gray-900" : "text-gray-500"
                    }`}
                  >
                    {check.text}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-6">
              <div className="border-t border-b border-gray-200 py-6">
                <h3 className="text-xl font-semibold mb-4">
                  Security Analysis Report
                </h3>
                <div className="space-y-3">
                  {report.findings.map((finding, index) => (
                    <div key={index} className="text-lg">
                      {finding}
                    </div>
                  ))}
                </div>
              </div>
              <div className="flex justify-center">
                <button
                  className="bg-indigo-600 text-white px-6 py-3 rounded-md text-lg font-semibold hover:bg-indigo-700 transition-colors"
                  onClick={() => (window.location.href = "/")}
                >
                  Back to Dashboard
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

ReactDOM.render(<Analysis />, document.getElementById("root"));
