import "./ReviewSection.scss";

export const ReviewSection = () => {
  return (
    <div className="container">
      <section className="reviews">
        <div className="reviews__title-box">
          <h2 className="reviews__title-box__title">Trusted by teams</h2>
        </div>

        <div className="reviews__card-box">
          <div className="reviews__card-box__card review-1"></div>
          <div className="reviews__card-box__card review-2"></div>
          <div className="reviews__card-box__card review-3"></div>
          <div className="reviews__card-box__card review-4"></div>
          <div className="reviews__card-box__card review-5"></div>
          <div className="reviews__card-box__card review-6"></div>
        </div>
      </section>
    </div>
  );
};
