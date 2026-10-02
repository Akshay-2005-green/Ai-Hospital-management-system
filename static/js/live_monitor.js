/* =========================================================
   LIVE QUEUE MONITOR
   ========================================================= */

/* Main Live Monitor Container */

.live-monitor-page {
    width: 100%;
}


/* =========================================================
   Live Monitor Header
   ========================================================= */

.live-monitor-header {
    display: flex;
    align-items: center;
    justify-content: space-between;

    margin-bottom: 25px;
}


.live-monitor-title h1 {
    font-size: 28px;
    margin-bottom: 7px;
    color: #263238;
}


.live-monitor-title p {
    color: #7a8989;
    font-size: 14px;
}


.live-monitor-meta {
    display: flex;
    flex-direction: column;
    align-items: flex-end;

    gap: 5px;
}


.live-monitor-time {
    font-size: 27px;
    font-weight: 600;
    color: #263238;
}


.live-monitor-date {
    color: #7a8989;
    font-size: 11px;

    text-transform: uppercase;
    letter-spacing: 1px;
}


/* =========================================================
   Live Status
   ========================================================= */

.live-status {
    display: inline-flex;

    align-items: center;
    gap: 7px;

    padding: 7px 12px;

    border-radius: 20px;

    background: #e9f8f5;

    color: #0b9f8f;

    font-size: 12px;

    font-weight: 600;
}


.live-status-dot {
    width: 8px;
    height: 8px;

    border-radius: 50%;

    background: #0b9f8f;
}


/* =========================================================
   Currently Serving Header
   ========================================================= */

.live-section-header {
    display: flex;

    align-items: center;

    justify-content: space-between;

    margin-bottom: 15px;
}


.live-section-title {
    display: flex;

    align-items: center;

    gap: 10px;
}


.live-section-title h2 {
    font-size: 18px;
    color: #263238;
}


.live-section-icon {
    width: 34px;
    height: 34px;

    display: flex;

    align-items: center;
    justify-content: center;

    border-radius: 8px;

    background: #e9f8f5;

    color: #0b9f8f;

    font-size: 17px;
}


/* =========================================================
   Currently Serving Cards
   ========================================================= */

.live-serving-grid {

    display: grid;

    grid-template-columns:
        repeat(3, 1fr);

    gap: 18px;

    margin-bottom: 25px;
}


.live-serving-card {

    background: white;

    border: 1px solid #e2ebeb;

    border-left: 4px solid #0b9f8f;

    border-radius: 12px;

    padding: 20px;

    min-height: 245px;

    box-shadow:
        0 3px 12px rgba(
            0,
            0,
            0,
            0.03
        );

    transition: 0.2s;
}


.live-serving-card:hover {

    transform: translateY(-2px);

    box-shadow:
        0 6px 18px rgba(
            0,
            0,
            0,
            0.06
        );
}


/* Department variations */

.live-serving-card.dental {

    border-left-color: #20a8b5;
}


.live-serving-card.pharmacy {

    border-left-color: #198754;
}


.live-serving-card.pediatric {

    border-left-color: #8b6bb5;
}


/* =========================================================
   Serving Card Top
   ========================================================= */

.live-serving-top {

    display: flex;

    align-items: center;

    justify-content: space-between;

    margin-bottom: 25px;
}


.live-department {

    display: inline-block;

    padding: 6px 10px;

    border-radius: 5px;

    background: #e9f8f5;

    color: #0b9f8f;

    font-size: 11px;

    font-weight: 700;

    text-transform: uppercase;

    letter-spacing: 0.5px;
}


.live-serving-card.dental
.live-department {

    background: #eaf8fa;

    color: #168e9b;
}


.live-serving-card.pharmacy
.live-department {

    background: #eaf7f0;

    color: #198754;
}


.live-serving-card.pediatric
.live-department {

    background: #f3eef9;

    color: #7955a6;
}


.live-room {

    color: #7a8989;

    font-size: 12px;
}


/* =========================================================
   Queue Number
   ========================================================= */

.live-queue-label {

    text-align: center;

    color: #899696;

    font-size: 10px;

    font-weight: 600;

    letter-spacing: 2px;

    margin-bottom: 5px;
}


.live-queue-number {

    text-align: center;

    font-size: 48px;

    font-weight: 700;

    color: #263238;

    letter-spacing: 1px;
}


/* =========================================================
   Serving Status
   ========================================================= */

.live-serving-footer {

    display: flex;

    align-items: center;

    justify-content: space-between;

    border-top: 1px solid #edf1f1;

    margin-top: 20px;

    padding-top: 13px;
}


.live-serving-status {

    display: flex;

    align-items: center;

    gap: 7px;

    color: #687878;

    font-size: 12px;
}


.live-status-indicator {

    width: 8px;
    height: 8px;

    border-radius: 50%;

    background: #0b9f8f;
}


/* =========================================================
   Complete / Action Button
   ========================================================= */

.live-action-button {

    width: 36px;
    height: 36px;

    border: none;

    border-radius: 50%;

    background: #e9f8f5;

    color: #0b9f8f;

    display: flex;

    align-items: center;
    justify-content: center;

    cursor: pointer;

    font-size: 15px;

    transition: 0.2s;
}


.live-action-button:hover {

    background: #0b9f8f;

    color: white;

}


/* =========================================================
   Waiting Queue Section
   ========================================================= */

.live-waiting-section {

    margin-top: 5px;
}


.live-waiting-grid {

    display: grid;

    grid-template-columns:
        repeat(4, 1fr);

    gap: 15px;
}


/* =========================================================
   Waiting Card
   ========================================================= */

.live-waiting-card {

    background: white;

    border: 1px solid #e2ebeb;

    border-radius: 12px;

    overflow: hidden;
}


.live-waiting-header {

    padding: 15px;

    display: flex;

    align-items: center;

    justify-content: space-between;

    border-bottom: 1px solid #edf1f1;
}


.live-waiting-header h3 {

    font-size: 13px;

    color: #526464;

    text-transform: uppercase;

    letter-spacing: 0.5px;
}


.live-waiting-count {

    padding: 5px 8px;

    border-radius: 5px;

    background: #f3f7f7;

    color: #718080;

    font-size: 10px;

    font-weight: 600;
}


/* =========================================================
   Call Next Button
   ========================================================= */

.live-next-button {

    border: none;

    background: #0b9f8f;

    color: white;

    padding: 7px 10px;

    border-radius: 6px;

    cursor: pointer;

    font-size: 10px;

    font-weight: 600;

    transition: 0.2s;
}


.live-next-button:hover {

    background: #087f72;

}


/* =========================================================
   Waiting Patient Row
   ========================================================= */

.live-waiting-patient {

    display: flex;

    align-items: center;

    gap: 10px;

    padding: 12px 15px;

    border-bottom: 1px solid #f0f3f3;
}


.live-waiting-patient:last-child {

    border-bottom: none;
}


.live-position {

    width: 29px;
    height: 29px;

    flex-shrink: 0;

    border: 1px solid #dce6e6;

    border-radius: 50%;

    display: flex;

    align-items: center;
    justify-content: center;

    color: #687878;

    font-size: 11px;
}


.live-patient-number {

    flex: 1;

    font-size: 13px;

    font-weight: 600;

    color: #344444;
}


.live-next-label {

    color: #0b9f8f;

    font-size: 10px;

    font-weight: 600;
}


.live-waiting-label {

    color: #929e9e;

    font-size: 10px;
}


/* =========================================================
   Announcement Bar
   ========================================================= */

.live-announcement {

    margin-top: 25px;

    background: #0b9f8f;

    color: white;

    border-radius: 10px;

    min-height: 50px;

    display: flex;

    align-items: center;

    overflow: hidden;
}


.live-announcement-title {

    height: 50px;

    display: flex;

    align-items: center;

    padding: 0 20px;

    background: #087f72;

    font-size: 11px;

    font-weight: 700;

    letter-spacing: 1px;
}


.live-announcement-text {

    padding: 0 20px;

    font-size: 13px;
}


/* =========================================================
   Empty Queue
   ========================================================= */

.live-empty-state {

    background: white;

    border: 1px solid #e2ebeb;

    border-radius: 12px;

    padding: 35px 20px;

    text-align: center;

    color: #718080;
}


.live-empty-state-icon {

    font-size: 35px;

    margin-bottom: 10px;
}


.live-empty-state h3 {

    color: #344444;

    margin-bottom: 6px;

    font-size: 16px;
}


.live-empty-state p {

    font-size: 13px;
}


/* =========================================================
   Loading State
   ========================================================= */

.live-loading {

    background: white;

    border: 1px solid #e2ebeb;

    border-radius: 12px;

    padding: 35px;

    text-align: center;

    color: #718080;

    font-size: 14px;
}


/* =========================================================
   Responsive Design
   ========================================================= */

@media (max-width: 1200px) {

    .live-serving-grid {

        grid-template-columns:
            repeat(2, 1fr);
    }


    .live-waiting-grid {

        grid-template-columns:
            repeat(2, 1fr);
    }

}


@media (max-width: 850px) {

    .main-content {

        margin-left: 0;

        padding: 25px;
    }


    .live-monitor-header {

        align-items: flex-start;

        gap: 15px;
    }


    .live-monitor-meta {

        align-items: flex-end;
    }


    .live-serving-grid {

        grid-template-columns: 1fr;
    }


    .live-waiting-grid {

        grid-template-columns: 1fr;
    }

}


@media (max-width: 600px) {

    .main-content {

        padding: 20px 15px;
    }


    .live-monitor-header {

        flex-direction: column;
    }


    .live-monitor-meta {

        align-items: flex-start;
    }


    .live-monitor-title h1 {

        font-size: 24px;
    }


    .live-queue-number {

        font-size: 42px;
    }


    .live-announcement {

        flex-direction: column;

        align-items: stretch;
    }


    .live-announcement-title {

        justify-content: center;
    }


    .live-announcement-text {

        padding: 12px 15px;

        text-align: center;
    }

}