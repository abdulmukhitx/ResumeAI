#!/usr/bin/env python3
"""
Modern Resume Processor - Unified Processing System
=================================================

Ultra-comprehensive resume processing system combining modern PDF extraction
and AI analysis with extensive error handling and prevention.

Features:
- Unified PDF extraction and AI analysis pipeline
- 8+ PDF engines with intelligent fallback
- 15+ AI providers with comprehensive analysis
- 2000+ skills database across all industries
- Complete error prevention and tracking system
- Performance optimization and caching
- ASCII-safe processing throughout
- Comprehensive logging and monitoring

Error Prevention System:
- UTF-8 encoding errors: Eliminated through ASCII-safe processing
- PDF processing errors: Multiple engine fallbacks
- AI API failures: Multiple provider fallbacks with retry logic
- Memory issues: Efficient processing and chunking
- Network timeouts: Configurable timeouts and retries
- Invalid responses: Validation and sanitization
- File corruption: Multiple parsing methods and repair
"""

import logging
import time
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime

# Import our modern components
from modern_pdf_processor import ModernPDFProcessor, ExtractionResult as PDFExtractionResult
from modern_ai_analyzer import ModernAIAnalyzer, AnalysisResult

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Comprehensive processing result combining PDF extraction and AI analysis."""
    
    # File information
    file_path: str
    file_size: int
    processing_time: float
    
    # PDF extraction results
    pdf_extraction_successful: bool
    pdf_extraction_method: str
    pdf_extraction_confidence: float
    extracted_text: str
    pdf_errors: List[str]
    pdf_warnings: List[str]
    
    # AI analysis results
    ai_analysis_successful: bool
    ai_analysis_method: str
    analysis_result: Optional[AnalysisResult]
    ai_errors: List[str]
    ai_warnings: List[str]
    
    # Overall results
    overall_success: bool
    overall_confidence: float
    processing_errors: List[str]
    processing_warnings: List[str]
    
    # Performance metrics
    pdf_processing_time: float
    ai_processing_time: float
    total_processing_time: float
    
    # Metadata
    metadata: Dict[str, Any]
    
    @property
    def success(self) -> bool:
        """Alias for overall_success for backward compatibility."""
        return self.overall_success
    
    @property
    def processing_method(self) -> str:
        """Combined processing method."""
        methods = []
        if self.pdf_extraction_method:
            methods.append(f"PDF:{self.pdf_extraction_method}")
        if self.ai_analysis_method:
            methods.append(f"AI:{self.ai_analysis_method}")
        return " + ".join(methods) if methods else "unknown"
    
    @property
    def extraction_method(self) -> str:
        """Alias for PDF extraction method."""
        return self.pdf_extraction_method
    
    @property
    def confidence_score(self) -> float:
        """Alias for overall_confidence."""
        return self.overall_confidence
    
    @property
    def resume_score(self) -> float:
        """Resume quality score based on analysis."""
        if self.analysis_result and hasattr(self.analysis_result, 'resume_score'):
            return self.analysis_result.resume_score
        return self.overall_confidence * 100
    
    @property
    def skills(self) -> List[str]:
        """Extracted skills from analysis."""
        if self.analysis_result and hasattr(self.analysis_result, 'skills'):
            return self.analysis_result.skills
        return []
    
    @property
    def experience_level(self) -> str:
        """Experience level from analysis."""
        if self.analysis_result and hasattr(self.analysis_result, 'experience_level'):
            return self.analysis_result.experience_level
        return "unknown"
    
    @property
    def job_titles(self) -> List[str]:
        """Job titles from analysis."""
        if self.analysis_result and hasattr(self.analysis_result, 'job_titles'):
            return self.analysis_result.job_titles
        return []
    
    @property
    def education(self) -> List[Dict[str, Any]]:
        """Education from analysis."""
        if self.analysis_result and hasattr(self.analysis_result, 'education'):
            return self.analysis_result.education
        return []
    
    @property
    def work_experience(self) -> List[Dict[str, Any]]:
        """Work experience from analysis."""
        if self.analysis_result and hasattr(self.analysis_result, 'work_experience'):
            return self.analysis_result.work_experience
        return []
    
    @property
    def summary(self) -> str:
        """Summary from analysis."""
        if self.analysis_result and hasattr(self.analysis_result, 'summary'):
            return self.analysis_result.summary
        return "No summary available"
    
    @property
    def error(self) -> str:
        """Combined error message."""
        all_errors = self.processing_errors + self.pdf_errors + self.ai_errors
        return "; ".join(all_errors) if all_errors else ""


class ProcessingPipeline:
    """Processing pipeline configuration."""
    
    def __init__(self):
        self.pdf_timeout = 60  # seconds
        self.ai_timeout = 120  # seconds
        self.max_retries = 3
        self.enable_caching = True
        self.enable_fallbacks = True
        self.log_detailed_errors = True


class ModernResumeProcessor:
    """
    Unified modern resume processor combining PDF extraction and AI analysis.
    """
    
    def __init__(self, pipeline_config: Optional[ProcessingPipeline] = None):
        """Initialize the modern resume processor."""
        self.config = pipeline_config or ProcessingPipeline()
        
        # Initialize components
        self.pdf_processor = ModernPDFProcessor()
        self.ai_analyzer = ModernAIAnalyzer()
        
        # Processing statistics
        self.processing_stats = {
            "total_processed": 0,
            "successful_extractions": 0,
            "successful_analyses": 0,
            "failed_extractions": 0,
            "failed_analyses": 0,
            "average_processing_time": 0.0,
            "error_patterns": {},
            "performance_metrics": {}
        }
        
        # Error tracking
        self.error_history = []
        self.performance_history = []
        
        logger.info("ModernResumeProcessor initialized successfully")
    
    def process_resume(self, file_path: Union[str, Path]) -> ProcessingResult:
        """
        Process resume with comprehensive PDF extraction and AI analysis.
        
        Args:
            file_path: Path to the resume file
            
        Returns:
            ProcessingResult with complete processing information
        """
        start_time = time.time()
        file_path = Path(file_path)
        
        logger.info(f"Starting resume processing: {file_path.name}")
        
        # Initialize result structure
        result = ProcessingResult(
            file_path=str(file_path),
            file_size=0,
            processing_time=0.0,
            pdf_extraction_successful=False,
            pdf_extraction_method="",
            pdf_extraction_confidence=0.0,
            extracted_text="",
            pdf_errors=[],
            pdf_warnings=[],
            ai_analysis_successful=False,
            ai_analysis_method="",
            analysis_result=None,
            ai_errors=[],
            ai_warnings=[],
            overall_success=False,
            overall_confidence=0.0,
            processing_errors=[],
            processing_warnings=[],
            pdf_processing_time=0.0,
            ai_processing_time=0.0,
            total_processing_time=0.0,
            metadata={}
        )
        
        try:
            # Get file information
            if file_path.exists():
                result.file_size = file_path.stat().st_size
            else:
                result.processing_errors.append("File does not exist")
                return self._finalize_result(result, start_time)
            
            # Step 1: PDF Text Extraction
            logger.info("Step 1: PDF text extraction")
            pdf_start_time = time.time()
            
            try:
                pdf_result = self.pdf_processor.extract_text(file_path)
                result.pdf_processing_time = time.time() - pdf_start_time
                
                if pdf_result and pdf_result.text.strip():
                    result.pdf_extraction_successful = True
                    result.pdf_extraction_method = pdf_result.method
                    result.pdf_extraction_confidence = pdf_result.confidence
                    result.extracted_text = pdf_result.text
                    result.pdf_errors = pdf_result.errors
                    result.pdf_warnings = pdf_result.warnings
                    
                    logger.info(f"PDF extraction successful: {pdf_result.method} "
                              f"(confidence: {pdf_result.confidence:.2f})")
                else:
                    result.pdf_errors.append("PDF extraction returned no text")
                    logger.warning("PDF extraction failed - no text extracted")
                    
            except Exception as e:
                result.pdf_processing_time = time.time() - pdf_start_time
                error_msg = f"PDF extraction failed: {str(e)}"
                result.pdf_errors.append(error_msg)
                logger.error(error_msg)
            
            # Step 2: AI Analysis (if PDF extraction was successful)
            if result.pdf_extraction_successful:
                logger.info("Step 2: AI resume analysis")
                ai_start_time = time.time()
                
                try:
                    analysis_result = self.ai_analyzer.analyze_resume_comprehensive(result.extracted_text)
                    result.ai_processing_time = time.time() - ai_start_time
                    
                    if analysis_result:
                        result.ai_analysis_successful = True
                        result.ai_analysis_method = analysis_result.processing_method
                        result.analysis_result = analysis_result
                        result.ai_errors = analysis_result.errors
                        result.ai_warnings = analysis_result.warnings
                        
                        logger.info(f"AI analysis successful: {analysis_result.processing_method} "
                                  f"(confidence: {analysis_result.confidence_score:.2f})")
                    else:
                        result.ai_errors.append("AI analysis returned no result")
                        logger.warning("AI analysis failed - no result returned")
                        
                except Exception as e:
                    result.ai_processing_time = time.time() - ai_start_time
                    error_msg = f"AI analysis failed: {str(e)}"
                    result.ai_errors.append(error_msg)
                    logger.error(error_msg)
            else:
                result.ai_errors.append("Skipped AI analysis due to PDF extraction failure")
                logger.info("Skipping AI analysis due to PDF extraction failure")
            
            # Step 3: Calculate overall success and confidence
            result = self._calculate_overall_metrics(result)
            
            # Step 4: Update processing statistics
            self._update_processing_stats(result)
            
            logger.info(f"Resume processing completed: success={result.overall_success}, "
                       f"confidence={result.overall_confidence:.2f}")
            
        except Exception as e:
            error_msg = f"Unexpected processing error: {str(e)}"
            result.processing_errors.append(error_msg)
            logger.error(error_msg)
        
        return self._finalize_result(result, start_time)
    
    def _calculate_overall_metrics(self, result: ProcessingResult) -> ProcessingResult:
        """Calculate overall success and confidence metrics."""
        
        # Overall success: both PDF extraction and AI analysis successful
        result.overall_success = result.pdf_extraction_successful and result.ai_analysis_successful
        
        # Overall confidence: weighted average of PDF and AI confidence
        if result.pdf_extraction_successful and result.ai_analysis_successful:
            pdf_weight = 0.3
            ai_weight = 0.7
            result.overall_confidence = (
                pdf_weight * result.pdf_extraction_confidence +
                ai_weight * result.analysis_result.confidence_score
            )
        elif result.pdf_extraction_successful:
            result.overall_confidence = result.pdf_extraction_confidence * 0.5  # Reduced without AI
        else:
            result.overall_confidence = 0.0
        
        # Add warnings for partial success
        if result.pdf_extraction_successful and not result.ai_analysis_successful:
            result.processing_warnings.append("PDF extraction successful but AI analysis failed")
        elif not result.pdf_extraction_successful:
            result.processing_warnings.append("PDF extraction failed - no analysis possible")
        
        return result
    
    def _update_processing_stats(self, result: ProcessingResult):
        """Update processing statistics."""
        self.processing_stats["total_processed"] += 1
        
        if result.pdf_extraction_successful:
            self.processing_stats["successful_extractions"] += 1
        else:
            self.processing_stats["failed_extractions"] += 1
        
        if result.ai_analysis_successful:
            self.processing_stats["successful_analyses"] += 1
        else:
            self.processing_stats["failed_analyses"] += 1
        
        # Update average processing time
        total_time = self.processing_stats.get("total_processing_time", 0.0)
        total_count = self.processing_stats["total_processed"]
        new_total_time = total_time + result.total_processing_time
        self.processing_stats["average_processing_time"] = new_total_time / total_count
        self.processing_stats["total_processing_time"] = new_total_time
        
        # Track error patterns
        for error in result.processing_errors + result.pdf_errors + result.ai_errors:
            error_type = self._categorize_error(error)
            self.processing_stats["error_patterns"][error_type] = (
                self.processing_stats["error_patterns"].get(error_type, 0) + 1
            )
        
        # Performance metrics
        self.performance_history.append({
            "timestamp": datetime.now().isoformat(),
            "file_size": result.file_size,
            "pdf_time": result.pdf_processing_time,
            "ai_time": result.ai_processing_time,
            "total_time": result.total_processing_time,
            "success": result.overall_success,
            "confidence": result.overall_confidence
        })
        
        # Keep only last 100 performance records
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-100:]
    
    def _categorize_error(self, error_message: str) -> str:
        """Categorize error for tracking patterns."""
        error_lower = error_message.lower()
        
        if "utf-8" in error_lower or "encoding" in error_lower:
            return "encoding_error"
        elif "timeout" in error_lower:
            return "timeout_error"
        elif "memory" in error_lower:
            return "memory_error"
        elif "network" in error_lower or "connection" in error_lower:
            return "network_error"
        elif "api" in error_lower:
            return "api_error"
        elif "pdf" in error_lower:
            return "pdf_error"
        elif "file" in error_lower:
            return "file_error"
        elif "json" in error_lower or "parsing" in error_lower:
            return "parsing_error"
        else:
            return "unknown_error"
    
    def _finalize_result(self, result: ProcessingResult, start_time: float) -> ProcessingResult:
        """Finalize processing result with timing and metadata."""
        result.total_processing_time = time.time() - start_time
        result.processing_time = result.total_processing_time
        
        # Add comprehensive metadata
        result.metadata.update({
            "processor_version": "1.0.0",
            "pdf_engines_available": len(self.pdf_processor.supported_engines),
            "ai_providers_available": len(self.ai_analyzer.ai_providers),
            "processing_timestamp": datetime.now().isoformat(),
            "file_name": Path(result.file_path).name,
            "text_length": len(result.extracted_text),
            "pdf_method_used": result.pdf_extraction_method,
            "ai_method_used": result.ai_analysis_method,
            "total_errors": len(result.processing_errors + result.pdf_errors + result.ai_errors),
            "total_warnings": len(result.processing_warnings + result.pdf_warnings + result.ai_warnings)
        })
        
        return result
    
    def process_resume_safe(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Safe processing method that returns a simplified dictionary result.
        Compatible with existing system interfaces.
        
        Args:
            file_path: Path to the resume file
            
        Returns:
            Dictionary with processing results
        """
        try:
            result = self.process_resume(file_path)
            
            # Convert to simplified format for backward compatibility
            return {
                "success": result.overall_success,
                "text": result.extracted_text,
                "analysis": asdict(result.analysis_result) if result.analysis_result else None,
                "confidence": result.overall_confidence,
                "method": f"{result.pdf_extraction_method} + {result.ai_analysis_method}",
                "errors": result.processing_errors + result.pdf_errors + result.ai_errors,
                "warnings": result.processing_warnings + result.pdf_warnings + result.ai_warnings,
                "processing_time": result.total_processing_time,
                "metadata": result.metadata
            }
            
        except Exception as e:
            logger.error(f"Safe processing failed: {e}")
            return {
                "success": False,
                "text": "",
                "analysis": None,
                "confidence": 0.0,
                "method": "error",
                "errors": [f"Processing failed: {str(e)}"],
                "warnings": [],
                "processing_time": 0.0,
                "metadata": {"error": True}
            }
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get comprehensive processing statistics."""
        return {
            "processing_stats": self.processing_stats,
            "pdf_processor_stats": self.pdf_processor.get_processing_stats(),
            "ai_analyzer_stats": self.ai_analyzer.get_analysis_statistics(),
            "recent_performance": self.performance_history[-10:] if self.performance_history else [],
            "error_summary": self._generate_error_summary(),
            "recommendations": self._generate_performance_recommendations()
        }
    
    def _generate_error_summary(self) -> Dict[str, Any]:
        """Generate error summary and prevention recommendations."""
        error_patterns = self.processing_stats.get("error_patterns", {})
        total_errors = sum(error_patterns.values())
        
        if total_errors == 0:
            return {"total_errors": 0, "recommendations": ["System running smoothly"]}
        
        # Calculate error percentages
        error_percentages = {
            error_type: (count / total_errors) * 100
            for error_type, count in error_patterns.items()
        }
        
        # Generate recommendations based on error patterns
        recommendations = []
        
        if error_percentages.get("encoding_error", 0) > 10:
            recommendations.append("Consider upgrading to newer PDF processing engines")
        
        if error_percentages.get("timeout_error", 0) > 15:
            recommendations.append("Increase processing timeouts for large files")
        
        if error_percentages.get("memory_error", 0) > 5:
            recommendations.append("Implement memory optimization for large files")
        
        if error_percentages.get("api_error", 0) > 20:
            recommendations.append("Review AI provider configurations and rate limits")
        
        return {
            "total_errors": total_errors,
            "error_patterns": error_patterns,
            "error_percentages": error_percentages,
            "recommendations": recommendations
        }
    
    def _generate_performance_recommendations(self) -> List[str]:
        """Generate performance optimization recommendations."""
        recommendations = []
        
        if not self.performance_history:
            return ["No performance data available yet"]
        
        # Analyze recent performance
        recent_times = [p["total_time"] for p in self.performance_history[-20:]]
        avg_time = sum(recent_times) / len(recent_times)
        
        if avg_time > 30:  # seconds
            recommendations.append("Processing time is high - consider optimizing or upgrading hardware")
        
        success_rate = sum(1 for p in self.performance_history[-20:] if p["success"]) / len(self.performance_history[-20:])
        
        if success_rate < 0.9:
            recommendations.append("Success rate is below 90% - review error patterns and configurations")
        
        # Check PDF vs AI processing time balance
        recent_pdf_times = [p["pdf_time"] for p in self.performance_history[-20:]]
        recent_ai_times = [p["ai_time"] for p in self.performance_history[-20:]]
        
        avg_pdf_time = sum(recent_pdf_times) / len(recent_pdf_times)
        avg_ai_time = sum(recent_ai_times) / len(recent_ai_times)
        
        if avg_pdf_time > avg_ai_time * 2:
            recommendations.append("PDF processing is bottleneck - consider faster extraction engines")
        elif avg_ai_time > avg_pdf_time * 3:
            recommendations.append("AI analysis is bottleneck - consider faster AI providers")
        
        return recommendations or ["Performance is optimal"]
    
    def clear_caches(self):
        """Clear all processing caches."""
        self.pdf_processor.clear_cache()
        if hasattr(self.ai_analyzer, 'cache'):
            self.ai_analyzer.cache.clear()
        
        logger.info("All processing caches cleared")
    
    def reset_statistics(self):
        """Reset processing statistics."""
        self.processing_stats = {
            "total_processed": 0,
            "successful_extractions": 0,
            "successful_analyses": 0,
            "failed_extractions": 0,
            "failed_analyses": 0,
            "average_processing_time": 0.0,
            "error_patterns": {},
            "performance_metrics": {}
        }
        self.error_history.clear()
        self.performance_history.clear()
        
        logger.info("Processing statistics reset")


# Backward compatibility classes
class ResumeProcessor:
    """Backward compatibility wrapper."""
    
    def __init__(self):
        self.processor = ModernResumeProcessor()
    
    def process_resume(self, file_path: str) -> Dict[str, Any]:
        """Backward compatible processing method."""
        return self.processor.process_resume_safe(file_path)


class ResumeProcessorV5:
    """Enhanced backward compatibility with V5 naming."""
    
    def __init__(self):
        self.processor = ModernResumeProcessor()
    
    def process_resume_comprehensive(self, file_path: str) -> Dict[str, Any]:
        """Comprehensive processing with full result."""
        result = self.processor.process_resume(file_path)
        return asdict(result)
    
    def process_resume_safe(self, file_path: str) -> Dict[str, Any]:
        """Safe processing with simplified result."""
        return self.processor.process_resume_safe(file_path)


if __name__ == "__main__":
    # Test the unified processor
    processor = ModernResumeProcessor()
    print("Modern Resume Processor initialized")
    
    # Example usage
    test_file = "test_resume.pdf"
    if Path(test_file).exists():
        result = processor.process_resume(test_file)
        print(f"Processing successful: {result.overall_success}")
        print(f"Overall confidence: {result.overall_confidence:.2f}")
        print(f"PDF method: {result.pdf_extraction_method}")
        print(f"AI method: {result.ai_analysis_method}")
        print(f"Total time: {result.total_processing_time:.2f}s")
        
        if result.analysis_result:
            print(f"Skills found: {len(result.analysis_result.skills)}")
            print(f"Experience level: {result.analysis_result.experience_level}")
    else:
        print(f"Test file {test_file} not found")
    
    # Show statistics
    stats = processor.get_processing_statistics()
    print(f"\nProcessing Statistics:")
    print(f"Total processed: {stats['processing_stats']['total_processed']}")
    print(f"Success rate: {stats['processing_stats']['successful_extractions']}/{stats['processing_stats']['total_processed']}")
