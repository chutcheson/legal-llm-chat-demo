import React, { useState } from 'react';
import './linear-inspired.css';

const InteractiveTextProcessor = () => {
  const [step, setStep] = useState(1);
  const [userText, setUserText] = useState('I have a client that is looking to incorporate a business in the United States. What kinds of issues should I think about?');
  const [templateParts, setTemplateParts] = useState([]);
  const [finalResponse, setFinalResponse] = useState('');
  const [prePIIResponse, setPrePIIResponse] = useState('');
  const [piiScanResponse, setPIIResponse] = useState({}); 
  const [llmResponse, setLlmResponse] = useState('');
  const [isChanging, setIsChanging] = useState(false);

  const processText = async (text) => {
    try {
      const response = await fetch('http://127.0.0.1:8000/process-text', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      });
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return await response.json();
    } catch (error) {
      console.error('Error:', error);
      throw error;
    }
  };

  const piiScan = async (text) => {
    try {
      const response = await fetch("http://127.0.0.1:8000/pii-scan", {
        method: 'POST', 
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text })
      })
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return await response.json();
    } catch (error) {
      console.error('Error:', error);
      throw error;
    }
  }

  const generateResponse = async (text) => {
    try {
      const response = await fetch('http://127.0.0.1:8000/generate-response', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      });
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      return data.response;
    } catch (error) {
      console.error('Error:', error);
      throw error;
    }
  };

  const changeStep = async (newStep) => {
    setIsChanging(true);
    if (newStep === 2) {
      try {
        const data = await processText(userText);
        setTemplateParts(data.parts);
      } catch (error) {
        console.error('Error processing text:', error);
        // Handle error in UI, e.g., show an error message to the user
        setIsChanging(false);
        return;
      }
    }if (newStep === 3) {
      const finalText = templateParts.map(part => 
        part.type === 'dropdown' ? part.selected : part.content
      ).join('');
      setPrePIIResponse(finalText)
      try {
        const data = await piiScan(finalText); 
        console.log(data)
        setPIIResponse(data); 
        setStep(newStep);
        setIsChanging(false);
      } catch (error) {

      }
    }
    setTimeout(() => {
      if(newStep != 3) {
        setStep(newStep);
        setIsChanging(false);
      }
      
    }, 300);
  };

  const handleDropdownChange = (index, value) => {
    setTemplateParts(prevParts => 
      prevParts.map((part, i) => 
        i === index ? { ...part, selected: value } : part
      )
    );
  };

  const renderTemplate = () => {
    return templateParts.map((part, index) => {
      if (part.type === 'text') {
        return <span key={index}>{part.content}</span>;
      } else if (part.type === 'dropdown') {
        return (
          <select
            key={index}
            value={part.selected}
            onChange={(e) => handleDropdownChange(index, e.target.value)}
          >
            {part.options.map((option, optionIndex) => (
              <option key={optionIndex} value={option}>
                {option}
              </option>
            ))}
          </select>
        );
      }
      return null;
    });
  };

  const renderPIIResults = () => {
    return (
      <div>
        <div>
          {prePIIResponse}
        </div>
        <div className='my-2 py-2 w-full border-t border-gray-500'>
        The prompt above {piiScanResponse.tagged === true ? 
        <div className='inline'>
            <div className='inline underline decoration-red-500 decoration-2 underline-offset-1'>fails</div> the PII scan. We suspect the clients: {piiScanResponse.clients.map((value, index) => {
              return (
                <div className='inline'>({index + 1}) {value} </div>
              )
            })} could be detected from the prompt.
          </div> : null}
          { piiScanResponse.tagged == false ?
            <div className='inline'><div className='inline underline decoration-green-500 decoration-2 underline-offset-1'>
            passes
          </div> the PII scan, we were unable to detect any client details from the prompt.</div> : null
          } 
        </div>
      </div>
    )
  }

  const handleTemplateSubmit = async () => {
    const finalText = templateParts.map(part => 
      part.type === 'dropdown' ? part.selected : part.content
    ).join('');
    setFinalResponse(finalText);
    try {
      const response = await generateResponse(finalText);
      setLlmResponse(response);
      changeStep(4);
    } catch (error) {
      console.error('Error generating response:', error);
      // Handle error in UI, e.g., show an error message to the user
    }
  };

  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <>
            <div className="step-title">Step 1: Enter Text</div>
            <textarea
              value={userText}
              onChange={(e) => setUserText(e.target.value)}
              placeholder="Enter your text here..."
              className="textarea"
            />
            <button className="button" onClick={() => changeStep(2)}>Submit Text</button>
          </>
        );
      case 2:
        return (
          <>
            <div className="step-title">Step 2: Select Options</div>
            <div className="template-container">{renderTemplate()}</div>
            <button className="button" onClick={() => changeStep(3)}>PII Scan</button>
          </>
        );
      case 3:
        return (
          <>
            <div className="step-title">Step 3: PII Results</div>
            <div className="template-container">{renderPIIResults()}</div>
            <button className="button" onClick={handleTemplateSubmit}>Get Legal Analysis</button>
          </>
        );
      // case 3:
      //   return (
      //     <>
      //       <div className="step-title">Step 3: Review and Submit</div>
      //       <p className="response-container">{finalResponse}</p>
      //       <button className="button" onClick={() => changeStep(4)}>Get Legal Analysis</button>
      //     </> 
      //   );
      case 4:
        return (
          <>
            <div className="step-title">Step 4: Legal Analysis</div>
            <h3 className="text-xl font-bold mb-2">Analysis Result:</h3>
            <p className="response-container">{llmResponse}</p>
            <button className="button" onClick={() => changeStep(1)}>Start Over</button>
          </>
        );
      default:
        return null;
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        {step === 1 ? 'Interactive Legal Assistant' : 
         step === 2 ? 'Customize Your Query' : 
         step === 3 ? 'PII Scan Results' : 
         step === 4 ? 'Review Your Query' : 
         'Legal Analysis'}
      </div>
      <div className={`card-content ${isChanging ? 'changing' : ''}`}>
        {renderStep()}
      </div>
    </div>
  );
};

export default InteractiveTextProcessor;
