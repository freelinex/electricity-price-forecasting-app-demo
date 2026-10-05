import "./WorkflowSection.scss";

export const WorkflowSection = () => {
  return (
    <div className="container">
      <section id="workflow" className="info-workflow">
        <div className="info-workflow__title-box">
          <h2 className="info-workflow__title-box__title">
            Everything required to move
            <br />
            from forecast to action
          </h2>
        </div>

        <div className="info-workflow__text-box">
          <p className="info-workflow__text-box__text">
            GridScope brings revisions, drivers, uncertainty
            <br />
            and market impact into one evidence-backed
            <br />
            workflow
          </p>
        </div>

        <div className="info-workflow__card-box">
          <div className="info-workflow__card-box__card sources"></div>

          <div className="info-workflow__card-box__card workspaces"></div>

          <div className="info-workflow__card-box__card revisions"></div>

          <div className="info-workflow__card-box__card card-wide prices"></div>
        </div>
      </section>
    </div>
  );
};
