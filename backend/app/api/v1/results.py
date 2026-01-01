"""Reporting endpoints for exporting mission evidence."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from ...schemas.results import EvidencePackResponse, ReportRequest, ReportResponse
from ...services.results_service import ResultsService, get_results_service
from ...pipelines.pdf_generator import generate_match_report


router = APIRouter()


@router.post("/export", response_model=ReportResponse)
async def generate_report(
    payload: ReportRequest,
    service: ResultsService = Depends(get_results_service),
) -> ReportResponse:
    """Generate a forensic report and return metadata for download."""

    return await service.generate_report(payload)


@router.post("/export/pdf/{job_id}")
async def generate_pdf_report(
    job_id: str,
    matches: list | None = None,
    timeline: list | None = None,
) -> FileResponse:
    """Generate and download a PDF report for a job."""
    try:
        pdf_path = generate_match_report(job_id, matches or [], timeline or [])
        if not pdf_path.exists():
            raise HTTPException(status_code=404, detail="Report not found")
        return FileResponse(
            str(pdf_path),
            media_type="application/pdf",
            filename=f"kaaval_report_{job_id}.pdf",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")


@router.get("/evidence_pack/{job_id}", response_model=EvidencePackResponse)
async def evidence_pack(
    job_id: str,
    service: ResultsService = Depends(get_results_service),
) -> EvidencePackResponse:
    """Retrieve the evidence pack containing matched frames and reconstructions."""

    return await service.get_evidence_pack(job_id)

