import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import Model from 'react-body-highlighter';

function BodyDiagram({ selectedMuscle, onSelect, type }) {
  const data = selectedMuscle
    ? [{ name: 'Selected', muscles: [selectedMuscle] }]
    : [];

  return (
    <Model
      data={data}
      type={type}
      style={{ width: '10rem' }}
      bodyColor="#333"
      highlightedColors={['#c44']}
      onClick={({ muscle }) => onSelect(muscle)}
    />
  );
}

function App() {
  const [selectedMuscle, setSelectedMuscle] = useState(null);

  window.selectMuscleFromHeatmap = (muscle) => {
    setSelectedMuscle(muscle);
    window.renderChart(muscle);
  };

  React.useEffect(() => {
    document.querySelectorAll('.label[data-muscle]').forEach(el => {
      el.classList.toggle('active', el.dataset.muscle === selectedMuscle);
    });
    if (selectedMuscle) {
      window.renderChart(selectedMuscle);
    }
  }, [selectedMuscle]);

  return (
    <div className="body-diagrams">
      <div className="body-diagram">
        <h3>Front</h3>
        <BodyDiagram
          selectedMuscle={selectedMuscle}
          onSelect={setSelectedMuscle}
          type="anterior"
        />
      </div>
      <div className="body-diagram">
        <h3>Back</h3>
        <BodyDiagram
          selectedMuscle={selectedMuscle}
          onSelect={setSelectedMuscle}
          type="posterior"
        />
      </div>
    </div>
  );
}

const root = createRoot(document.getElementById('body-container'));
root.render(<App />);
