import "./MarketSection.scss";

export const MarketSection = () => {
  return (
    <div className="container">
      <section id="market" className="info-market">
        <div className="info-market__title-box">
          <h2 className="info-market__title-box__title">Complex market data</h2>
        </div>

        <div className="info-market__text-box">
          <p className="info-market__text-box__text">
            The experience is structured around the questions
            <br />
            electricity-market users ask under time pressure
          </p>
        </div>

        <div className="info-market__card-box">
          <div className="info-market__card-box__card card-1">
            <div className="info-market__card-box__card__title-box">
              <h4 className="info-market__card-box__card__title-box__title">
                Monitor
              </h4>
              <p className="info-market__card-box__card__title-box__text">
                What changed since the previous forecast?
              </p>
            </div>
          </div>

          <div className="info-market__card-box__card card-2">
            <div className="info-market__card-box__card__title-box">
              <h4 className="info-market__card-box__card__title-box__title">
                Explain
              </h4>
              <p className="info-market__card-box__card__title-box__text">
                Which drivers caused the movement?
              </p>
            </div>
          </div>

          <div className="info-market__card-box__card card-3">
            <div className="info-market__card-box__card__title-box">
              <h4 className="info-market__card-box__card__title-box__title">
                Act
              </h4>
              <p className="info-market__card-box__card__title-box__text">
                Does the change require a decision now?
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
