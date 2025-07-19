from typing import Union, Dict, Any
import streamlit as st
from dataclasses import dataclass

@dataclass
class DatabaseError:
    error_type: str
    message: str
    details: Dict[str, Any] = None

class ErrorHandler:
    @staticmethod
    def handle_db_error(error: Exception) -> DatabaseError:
        error_str = str(error).lower()
        
        if 'connection' in error_str:
            return DatabaseError(
                error_type='connection_error',
                message='Unable to connect to database',
                details={'original_error': str(error)}
            )
        elif 'permission' in error_str or 'privilege' in error_str:
            return DatabaseError(
                error_type='permission_error',
                message='Insufficient permissions to perform this operation',
                details={'original_error': str(error)}
            )
        elif 'syntax' in error_str:
            return DatabaseError(
                error_type='syntax_error',
                message='SQL syntax error in query',
                details={'original_error': str(error)}
            )
        elif 'duplicate' in error_str:
            return DatabaseError(
                error_type='duplicate_error',
                message='Duplicate entry found',
                details={'original_error': str(error)}
            )
        else:
            return DatabaseError(
                error_type='unknown_error',
                message='An unexpected error occurred',
                details={'original_error': str(error)}
            )

    @staticmethod
    def display_error(error: DatabaseError):
        # Do not display any error box in the UI
        pass

    @staticmethod
    def handle_and_display(error: Exception):
        db_error = ErrorHandler.handle_db_error(error)
        # Do not display any error box in the UI
        pass