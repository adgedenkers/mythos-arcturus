# Stream: MNE

## Modules

- Voice Memo Pipeline

---

# MNE (MNEMOS) Stream Architecture Overview  
**Stream Purpose:**  
The MNE (MNEMOS) stream in the Mythos system is dedicated to managing memory, voice memo ingestion, and recall systems. It serves as the foundational layer for capturing, synchronizing, and tracking voice-based memory inputs, ensuring reliable cross-device synchronization and metadata integrity. The stream acts as the entry point for raw voice data before it is processed, stored, or integrated into broader memory systems.  

---

## **Core Architecture**  
The MNE stream is structured around the **Voice Memo Pipeline** module, which handles the ingestion and synchronization of voice memos. This module is designed to work in tandem with external services (e.g., Syncthing) and downstream processing systems to ensure seamless integration into the Mythos memory ecosystem.  

### **Module Interactions**  
1. **Voice Memo Pipeline (MNE):**  
   - Acts as the **ingestion gateway** for voice memos.  
   - Uses **Syncthing** for cross-device synchronization and a **versioned manifest file** (`.rode-manifest.json`) to track metadata.  
   - Passively configures synchronization and metadata tracking via static files, with no active processing logic.  

2. **Downstream Systems (e.g., LOG, SEN, or future MNE modules):**  
   - Monitor the manifest file to detect new/changed voice memos.  
   - Trigger processing workflows (e.g., transcription, archival, or semantic tagging).  
   - May integrate with memory storage/retrieval systems for long-term persistence.  

---

## **Data Flow**  
1. **Ingestion:**  
   - Voice memos are deposited into the `voice_memos/incoming/` directory.  
   - Syncthing synchronizes files across devices using the folder marker file (`.stfolder/syncthing-folder-992cf5.txt`).  

2. **Metadata Tracking:**  
   - The `.rode-manifest.json` file is updated with metadata (e.g., `mtime`, `size`, `checksum`) for each file.  
   - The manifest is versioned to support schema evolution.  

3. **Processing Integration:**  
   - Downstream systems (e.g., LOGOS for knowledge orchestration) read the manifest to identify new/changed files.  
   - Files are moved to archival storage or processed further (not yet implemented in the current module).  

---

## **Key Architectural Patterns**  
1. **Manifest Pattern:**  
   - A versioned JSON manifest tracks file metadata, enabling efficient change detection without full directory scans.  
   - Supports future enhancements like conflict resolution and versioning.  

2. **Passive Configuration:**  
   - All components (e.g., Syncthing folder marker, manifest file) are static configuration files with no active logic.  
   - Simplifies deployment and reduces runtime dependencies.  

3. **Synchronization Marker Pattern:**  
   - A `.stfolder` text file explicitly identifies the directory as a Syncthing synchronization target.  
   - Ensures deterministic folder configuration across devices.  

4. **Decoupled Ingestion and Processing:**  
   - The pipeline separates ingestion (synchronization + metadata) from downstream processing, enabling modular scalability.  

---

## **Dependencies**  
- **Syncthing Service:** Required for cross-device synchronization of voice memos.  
- **File System:** Relies on standard file operations for storage.  
- **Downstream Processing Systems:** Modules in other streams (e.g., LOG for orchestration, SEN for perception) depend on the manifest to trigger workflows.  

---

## **Configuration**  
1. **Syncthing Folder Marker:**  
   - Folder ID (`v5gm9-jjumm`) and creation timestamp are embedded in `.stfolder/syncthing-folder-992cf5.txt`.  
   - Syncthing must be configured to recognize this folder and synchronize it across devices.  

2. **Manifest File:**  
   - Initial manifest schema is versioned (`version: 1`) and tracks files via a nested JSON structure.  
   - Example:  
     ```json
     {
       "version": 1,
       "files": {
         "20260301-voice-memo-001.wav": {
           "mtime": "2026-03-01T10:00:00Z",
           "size": 1234567,
           "checksum": "sha256:abcdef1234567890..."
         }
       }
     }
     ```  

---

## **Future Enhancements**  
1. **Automated Manifest Updates:**  
   - Automatically update `.rode-manifest.json` when files are added/modified.  
   - Implement conflict resolution for synchronized files.  

2. **Integration with Media Processing:**  
   - Connect to transcription or metadata extraction pipelines (e.g., in LOG or SEN streams).  
   - Add versioning for file changes and archival workflows.  

3. **Memory System Expansion:**  
   - Extend MNE to include recall mechanisms (e.g., querying voice memos by timestamp, keywords, or context).  
   - Integrate with long-term memory storage (e.g., indexed databases or semantic graphs).  

---

## **Summary**  
The MNE stream is a foundational layer for voice-based memory ingestion in Mythos, prioritizing reliability, synchronization, and modularity. The Voice Memo Pipeline module establishes a passive, configuration-driven architecture for tracking and synchronizing raw voice data, while future modules will expand into memory storage, retrieval, and semantic integration. By decoupling ingestion from processing and leveraging external services like Syncthing, the stream ensures scalability and adaptability for evolving memory systems.
