# winfsp/winfsp.h

WinFsp User Mode API.

In order to use the WinFsp API the user mode file system must include <winfsp/winfsp.h>
and link with the winfsp\_x64.dll (or winfsp\_x86.dll) library.

## FILE SYSTEM

A user mode file system is a program that uses the WinFsp API to expose a file system to
Windows. The user mode file system must implement the operations in FSP\_FILE\_SYSTEM\_INTERFACE,
create a file system object using FspFileSystemCreate and start its dispatcher using
FspFileSystemStartDispatcher. At that point it will start receing file system requests on the
FSP\_FILE\_SYSTEM\_INTERFACE operations.

### Classes

<details>
<summary>
<b>FSP_FILE_SYSTEM_INTERFACE</b> - File system interface.
</summary>
<blockquote>
<br/>

**Discussion**

The operations in this interface must be implemented by the user mode
file system.

#### Member Functions

<details>
<summary>
<b>CanDelete</b> - Determine whether a file or directory can be deleted.
</summary>
<blockquote>
<br/>

```c
NTSTATUS ( *CanDelete)(
    FSP_FILE_SYSTEM *FileSystem, 
    FSP_FSCTL_TRANSACT_REQ *Request, 
    PVOID FileNode,
    PWSTR FileName);  
```

**Parameters**

- _FileSystem_ \- The file system on which this request is posted.
- _Request_ \- The request posted by the kernel mode FSD.
- _FileNode_ \- The file node of the file or directory to test for deletion.
- _FileName_ \- The name of the file or directory to test for deletion.

**Return Value**

STATUS\_SUCCESS or error code.

**Discussion**

This function tests whether a file or directory can be safely deleted. This function does
not need to perform access checks, but may performs tasks such as check for empty
directories, etc.

This function should **NEVER** delete the file or directory in question. Deletion should
happen during Cleanup with Delete==TRUE.

This function gets called when Win32 API's such as DeleteFile or RemoveDirectory are used.
It does not get called when a file or directory is opened with FILE\_DELETE\_ON\_CLOSE.

**See Also**

- Cleanup


</blockquote>
</details>

<details>
<summary>
<b>Cleanup</b> - Cleanup a file.
</summary>
<blockquote>
<br/>

```c
VOID ( *Cleanup)(
    FSP_FILE_SYSTEM *FileSystem, 
    FSP_FSCTL_TRANSACT_REQ *Request, 
    PVOID FileNode,
    PWSTR FileName,
    BOOLEAN Delete);  
```

**Parameters**

- _FileSystem_ \- The file system on which this request is posted.
- _Request_ \- The request posted by the kernel mode FSD.
- _FileNode_ \- The file node of the file or directory to cleanup.
- _FileName_ \- The name of the file or directory to cleanup. Sent only when a Delete is requested.
- _Delete_ \- Determines whether to delete the file. Note that there is no way to report failure of
this operation. Also note that when this parameter is TRUE this is the last outstanding
cleanup for this particular file node.

**Discussion**

When CreateFile is used to open or create a file the kernel creates a kernel mode file
object (type FILE\_OBJECT) and a handle for it, which it returns to user-mode. The handle may
be duplicated (using DuplicateHandle), but all duplicate handles always refer to the same
file object. When all handles for a particular file object get closed (using CloseHandle)
the system sends a Cleanup request to the file system.

There will be a Cleanup operation for every Create or Open operation posted to the user mode
file system. However the Cleanup operation is **not** the final close operation on a file. The
file system must be ready to receive additional operations until close time. This is true
even when the file is being deleted!

An important function of the Cleanup operation is to complete a delete operation. Deleting
a file or directory in Windows is a three-stage process where the file is first opened, then
tested to see if the delete can proceed and if the answer is positive the file is then
deleted during Cleanup.

**See Also**

- Close
- CanDelete


</blockquote>
</details>

<details>
<summary>
<b>Close</b> - Close a file.
</summary>
<blockquote>
<br/>

```c
VOID ( *Close)(
    FSP_FILE_SYSTEM *FileSystem, 
    FSP_FSCTL_TRANSACT_REQ *Request, 
    PVOID FileNode);  
```

**Parameters**

- _FileSystem_ \- The file system on which this request is posted.
- _Request_ \- The request posted by the kernel mode FSD.
- _FileNode_ \- The file node of the file or directory to be closed.


</blockquote>
</details>

<details>
<summary>
<b>Create</b> - Create new file or directory.
</summary>
<blockquote>
<br/>

```c
NTSTATUS ( *Create)(
    FSP_FILE_SYSTEM *FileSystem, 
    FSP_FSCTL_TRANSACT_REQ *Request, 
    PWSTR FileName,
    BOOLEAN CaseSensitive,
    UINT32 CreateOptions, 
    UINT32 FileAttributes,
    PSECURITY_DESCRIPTOR SecurityDescriptor,
    UINT64 AllocationSize, 
    PVOID *PFileNode,
    FSP_FSCTL_FILE_INFO *FileInfo);  
```

**Parameters**

- _FileSystem_ \- The file system on which this request is posted.
- _Request_ \- The request posted by the kernel mode FSD.
- _FileName_ \- The name of the file or directory to be created.
- _CaseSensitive_ \- Whether to treat the FileName as case-sensitive or case-insensitive. Case-sensitive
file systems always treat FileName as case-sensitive regardless of this parameter.
- _CreateOptions_ \- Create options for this request. This parameter has the same meaning as the
CreateOptions parameter of the NtCreateFile API. User mode file systems should typically
only be concerned with the flag FILE\_DIRECTORY\_FILE, which is an instruction to create a
directory rather than a file. Some file systems may also want to pay attention to the
FILE\_NO\_INTERMEDIATE\_BUFFERING and FILE\_WRITE\_THROUGH flags, although these are
typically handled by the FSD component.
- _FileAttributes_ \- File attributes to apply to the newly created file or directory.
- _SecurityDescriptor_ \- Security descriptor to apply to the newly created file or directory. This security
descriptor will always be in self-relative format. Its length can be retrieved using the
Windows GetSecurityDescriptorLength API.
- _AllocationSize_ \- Allocation size for the newly created file.
- _PFileNode_ \- [out]
Pointer that will receive the file node on successful return from this call. The file
node is a void pointer (or an integer that can fit in a pointer) that is used to
uniquely identify an open file. Opening the same file name should always return the same
file node value for as long as the file with that name remains open anywhere in the
system. The file system can place any value it needs here.
- _FileInfo_ \- [out]
Pointer to a structure that will receive the file information on successful return
from this call. This information includes file attributes, file times, etc.

**Return Value**

STATUS\_SUCCESS or error code.


</blockquote>
</details>

<details>
<summary>
<b>Flush</b> - Flush a file or volume.
</summary>
<blockquote>
<br/>

```c
NTSTATUS ( *Flush)(
    FSP_FILE_SYSTEM *FileSystem, 
    FSP_FSCTL_TRANSACT_REQ *Request, 
    PVOID FileNode);  
```

**Parameters**

- _FileSystem_ \- The file system on which this request is posted.
- _Request_ \- The request posted by the kernel mode FSD.
- _FileNode_ \- The file node of the file to be flushed. When NULL the whole volume is being flushed.

**Return Value**

STATUS\_SUCCESS or error code.

**Discussion**

Note that the FSD will also flush all file/volume caches prior to invoking this operation.


</blockquote>
</details>

<details>
<summary>
<b>GetFileInfo</b> - Get file or directory information.
</summary>
<blockquote>
<br/>

```c
NTSTATUS ( *GetFileInfo)(
    FSP_FILE_SYSTEM *FileSystem, 
    FSP_FSCTL_TRANSACT_REQ *Request, 
    PVOID FileNode, 
    FSP_FSCTL_FILE_INFO *FileInfo);  
```

**Parameters**

- _FileSystem_ \- The file system on which this request is posted.
- _Request_ \- The request posted by the kernel mode FSD.
- _FileNode_ \- The file node of the file or directory to get information for.
- _FileInfo_ \- [out]
Pointer to a structure that will receive the file information on successful return
from this call. This information includes file attributes, file times, etc.

**Return Value**

STATUS\_SUCCESS or error code.


</blockquote>
</details>

<details>
<summary>
<b>GetReparsePoint</b> - Get reparse point.
</summary>
<blockquote>
<br/>

```c
NTSTATUS ( *GetReparsePoint)(
    FSP_FILE_SYSTEM *FileSystem, 
    FSP_FSCTL_TRANSACT_REQ *Request, 
    PVOID FileNode, 
    PWSTR FileName,
    PVOID Buffer,
    PSIZE_T PSize);  
```

**Parameters**

- _FileSystem_ \- The file system on which this request is posted.
- _Request_ \- The request posted by the kernel mode FSD.
- _FileNode_ \- The file node of the reparse point.
- _FileName_ \- The file name of the reparse point.
- _Buffer_ \- Pointer to a buffer that will receive the results of this operation.
- _PSize_ \- [in,out]
Pointer to the buffer size. On input it contains the size of the buffer.
On output it will contain the actual size of data copied.

**Return Value**

STATUS\_SUCCESS or error code.

**Discussion**

The behavior of this function depends on the value of FSP\_FSCTL\_VOLUME\_PARAMS ::
SymbolicLinksOnly. If the value of SymbolicLinksOnly is FALSE the file system
support full reparse points and this function is expected to fill the buffer
with a full reparse point. If the value of SymbolicLinksOnly is TRUE the file
system supports symbolic links only as reparse points and this function is
expected to fill the buffer with the symbolic link path.

**See Also**

- SetReparsePoint


</blockquote>
</details>

<details>
<summary>
<b>GetSecurity</b> - Get file or directory security descriptor.
</summary>
<blockquote>
<br/>

```c
NTSTATUS ( *GetSecurity)(
    FSP_FILE_SYSTEM *FileSystem, 
    FSP_FSCTL_TRANSACT_REQ *Request, 
    PVOID FileNode, 
    PSECURITY_DESCRIPTOR SecurityDescriptor,
    SIZE_T *PSecurityDescriptorSize);  
```

**Parameters**

- _FileSystem_ \- The file system on which this request is posted.
- _FileNode_ \- The file node of the file or directory to get the security descriptor for.
- _SecurityDescriptor_ \- Pointer to a buffer that will receive the file security descriptor on successful return
from this call. May be NULL.
- _PSecurityDescriptorSize_ \- [in,out]
Pointer to the security descriptor buffer size. On input it contains the size of the
security descriptor buffer. On output it will contain the actual size of the security
descriptor copied into the security descriptor buffer. Cannot be NULL.

**Return Value**

STATUS\_SUCCESS or error code.


</blockquote>
</details>

<details>
<summary>
<b>GetSecurityByName</b> - Get file or directory attributes and security descriptor given a file name.
</summary>
<blockquote>
<br/>

```c
NTSTATUS ( *GetSecurityByName)(
    FSP_FILE_SYSTEM *FileSystem, 
    PWSTR FileName,
    PUINT32 PFileAttributes, 
    PSECURITY_DESCRIPTOR SecurityDescriptor,
    SIZE_T *PSecurityDescriptorSize);  
```

**Parameters**

- _FileSystem_ \- The file system on which this request is posted.
- _FileName_ \- The name of the file or directory to get the attributes and security descriptor for.
- _PFileAttributes_ \- Pointer to a memory location that will receive the file attributes on successful return
from this call. May be NULL.
- _SecurityDescriptor_ \- Pointer to a buffer that will receive the file security descriptor on successful return
from this call. May be NULL.
- _PSecurityDescriptorSize_ \- [in,out]
Pointer to the security descriptor buffer size. On input it contains the size of the
security descriptor buffer. On output it will contain the actual size of the security
descriptor copied into the security descriptor buffer. May be NULL.

**Return Value**

STATUS\_SUCCESS, STATUS\_REPARSE or error code.

STATUS\_REPARSE should be returned by file systems that support reparse points when
they encounter a FileName that contains reparse points anywhere but the final path
component.


</blockquote>
</details>

<details>
<summary>
<b>GetVolumeInfo</b> - Get volume information.
</summary>
<blockquote>
<br/>

```c
NTSTATUS ( *GetVolumeInfo)(
    FSP_FILE_SYSTEM *FileSystem, 
    FSP_FSCTL_TRANSACT_REQ *Request, 
    FSP_FSCTL_VOLUME_INFO *VolumeInfo);  
```

**Parameters**

- _FileSystem_ \- The file system on which this request is posted.
- _Request_ \- The request posted by the kernel mode FSD.
- _VolumeInfo_ \- [out]
Pointer to a structure that will receive the volume information on successful return
from this call.

**Return Value**

STATUS\_SUCCESS or error code.


</blockquote>
</details>

<details>
<summary>
<b>Open</b> - Open a file or directory.
</summary>
<blockquote>
<br/>

```c
NTSTATUS ( *Open)(
    FSP_FILE_SYSTEM *FileSystem, 
    FSP_FSCTL_TRANSACT_REQ *Request, 
    PWSTR FileName,
    BOOLEAN CaseSensitive,
    UINT32 CreateOptions, 
    PVOID *PFileNode,
    FSP_FSCTL_FILE_INFO *FileInfo);  
```

**Parameters**

- _FileSystem_ \- The file system on which this request is posted.
- _Request_ \- The request posted by the kernel mode FSD.
- _FileName_ \- The name of the file or directory to be opened.
- _CaseSensitive_ \- Whether to treat the FileName as case-sensitive or case-insensitive. Case-sensitive
file systems always treat FileName as case-sensitive regardless of this parameter.
- _CreateOptions_ \- Create options for this request. This parameter has the same meaning as the
CreateOptions parameter of the NtCreateFile API. User mode file systems typically
do not need to do anything special with respect to this parameter. Some file systems may
also want to pay attention to the FILE\_NO\_INTERMEDIATE\_BUFFERING and FILE\_WRITE\_THROUGH
flags, although these are typically handled by the FSD component.
- _PFileNode_ \- [out]
Pointer that will receive the file node on successful return from this call. The file
node is a void pointer (or an integer that can fit in a pointer) that is used to
uniquely identify an open file. Opening the same file name should always return the same
file node value for as long as the file with that name remains open anywhere in the
system. The file system can place any value it needs here.
- _FileInfo_ \- [out]
Pointer to a structure that will receive the file information on successful return
from this call. This information includes file attributes, file times, etc.

**Return Value**

STATUS\_SUCCESS or error code.


</blockquote>
</details>

<details>
<summary>
<b>Overwrite</b> - Overwrite a file.
</summary>
<blockquote>
<br/>

```c
NTSTATUS ( *Overwrite)(
    FSP_FILE_SYSTEM *FileSystem, 
    FSP_FSCTL_TRANSACT_REQ *Request, 
    PVOID FileNode,
    UINT32 FileAttributes,
    BOOLEAN ReplaceFileAttributes, 
    FSP_FSCTL_FILE_INFO *FileInfo);  
```

**Parameters**

- _FileSystem_ \- The file system on which this request is posted.
- _Request_ \- The request posted by the kernel mode FSD.
- _FileNode_ \- The file node of the file to overwrite.
- _FileAttributes_ \- File attributes to apply to the overwritten file.
- _ReplaceFileAttributes_ \- When TRUE the existing file attributes should be replaced with the new ones.
When FALSE the existing file attributes should be merged (or'ed) with the new ones.
- _FileInfo_ \- [out]
Pointer to a structure that will receive the file information on successful return
from this call. This information includes file attributes, file times, etc.

**Return Value**

STATUS\_SUCCESS or error code.


</blockquote>
</details>

<details>
<summary>
<b>Read</b> - Read a file.
</summary>
<blockquote>
<br/>

```c
NTSTATUS ( *Read)(
    FSP_FILE_SYSTEM *FileSystem, 
    FSP_FSCTL_TRANSACT_REQ *Request, 
    PVOID FileNode,
    PVOID Buffer,
    UINT64 Offset,
    ULONG Length, 
    PULONG PBytesTransferred);  
```

**Parameters**

- _FileSystem_ \- The file system on which this request is posted.
- _Request_ \- The request posted by the kernel mode FSD.
- _FileNode_ \- The file node of the file to be read.
- _Buffer_ \- Pointer to a buffer that will receive the results of the read operation.
- _Offset_ \- Offset within the file to read from.
- _Length_ \- Length of data to read.
- _PBytesTransferred_ \- [out]
Pointer to a memory location that will receive the actual number of bytes read.

**Return Value**

STATUS\_SUCCESS or error code. STATUS\_PENDING is supported allowing for asynchronous
operation.


</blockquote>
</details>

<details>
<summary>
<b>ReadDirectory</b> - Read a directory.
</summary>
<blockquote>
<br/>

```c
NTSTATUS ( *ReadDirectory)(
    FSP_FILE_SYSTEM *FileSystem, 
    FSP_FSCTL_TRANSACT_REQ *Request, 
    PVOID FileNode,
    PVOID Buffer,
    UINT64 Offset,
    ULONG Length, 
    PWSTR Pattern, 
    PULONG PBytesTransferred);  
```

**Parameters**

- _FileSystem_ \- The file system on which this request is posted.
- _Request_ \- The request posted by the kernel mode FSD.
- _FileNode_ \- The file node of the directory to be read.
- _Buffer_ \- Pointer to a buffer that will receive the results of the read operation.
- _Offset_ \- Offset within the directory to read from. The kernel does not interpret this value
which is used solely by the file system to locate directory entries. However the
special value 0 indicates that the read should start from the first entries. The first
two entries returned by ReadDirectory should always be the "." and ".." entries.
- _Length_ \- Length of data to read.
- _Pattern_ \- The pattern to match against files in this directory. Can be NULL. The file system
can choose to ignore this parameter as the FSD will always perform its own pattern
matching on the returned results.
- _PBytesTransferred_ \- [out]
Pointer to a memory location that will receive the actual number of bytes read.

**Return Value**

STATUS\_SUCCESS or error code. STATUS\_PENDING is supported allowing for asynchronous
operation.

**See Also**

- FspFileSystemAddDirInfo


</blockquote>
</details>

<details>
<summary>
<b>Rename</b> - Renames a file or directory.
</summary>
<blockquote>
<br/>

```c
NTSTATUS ( *Rename)(
    FSP_FILE_SYSTEM *FileSystem, 
    FSP_FSCTL_TRANSACT_REQ *Request, 
    PVOID FileNode, 
    PWSTR FileName,
    PWSTR NewFileName,
    BOOLEAN ReplaceIfExists);  
```

**Parameters**

- _FileSystem_ \- The file system on which this request is posted.
- _Request_ \- The request posted by the kernel mode FSD.
- _FileNode_ \- The file node of the file or directory to be renamed.
- _FileName_ \- The current name of the file or directory to rename.
- _NewFileName_ \- The new name for the file or directory.
- _ReplaceIfExists_ \- Whether to replace a file that already exists at NewFileName.

**Return Value**

STATUS\_SUCCESS or error code.

**Discussion**

The kernel mode FSD provides certain guarantees prior to posting a rename operation:

- A file cannot be renamed if it has any open handles, other than the one used to perform
the rename.


- A file cannot be renamed if a file with the same name exists and has open handles.


- A directory cannot be renamed if it or any of its subdirectories contains a file that
has open handles.


</blockquote>
</details>

<details>
<summary>
<b>ResolveReparsePoints</b> - Resolve reparse points.
</summary>
<blockquote>
<br/>

```c
NTSTATUS ( *ResolveReparsePoints)(
    FSP_FILE_SYSTEM *FileSystem, 
    PWSTR FileName,
    BOOLEAN OpenReparsePoint, 
    PIO_STATUS_BLOCK PIoStatus,
    PVOID Buffer,
    PSIZE_T PSize);  
```

**Parameters**

- _FileSystem_ \- The file system on which this request is posted.
- _FileName_ \- The name of the file or directory to have its reparse points resolved.
- _OpenReparsePoint_ \- If TRUE, the last path component of FileName should not be resolved, even
if it is a reparse point that can be resolved. If FALSE, all path components
should be resolved if possible.
- _PIoStatus_ \- Pointer to storage that will receive the status to return to the FSD. When
this function succeeds it must set PIoStatus->Status to STATUS\_REPARSE and
PIoStatus->Information to either IO\_REPARSE or the reparse tag.
- _Buffer_ \- Pointer to a buffer that will receive the resolved file name (IO\_REPARSE) or
reparse data (reparse tag).
- _PSize_ \- [in,out]
Pointer to the buffer size. On input it contains the size of the buffer.
On output it will contain the actual size of data copied.

**Return Value**

STATUS\_REPARSE or error code.

**Discussion**

A file or directory can contain a reparse point. A reparse point is data that has
special meaning to the file system, Windows or user applications. For example, NTFS
and Windows use reparse points to implement symbolic links. As another example,
a particular file system may use reparse points to emulate UNIX FIFO's.

Reparse points are a general mechanism for attaching special behavior to files. WinFsp
supports any kind of reparse point. The symbolic link reparse point however is so
important for many file systems (especially POSIX ones) that WinFsp implements special
support for it.

This function is expected to resolve as many reparse points as possible. If a reparse
point is encountered that is not understood by the file system further reparse point
resolution should stop; the reparse point data should be returned to the FSD with status
STATUS\_REPARSE/reparse-tag. If a reparse point (symbolic link) is encountered that is
understood by the file system but points outside it, the reparse point should be
resolved, but further reparse point resolution should stop; the resolved file name
should be returned to the FSD with status STATUS\_REPARSE/IO\_REPARSE.


</blockquote>
</details>

<details>
<summary>
<b>SetBasicInfo</b> - Set file or directory basic information.
</summary>
<blockquote>
<br/>

```c
NTSTATUS ( *SetBasicInfo)(
    FSP_FILE_SYSTEM *FileSystem, 
    FSP_FSCTL_TRANSACT_REQ *Request, 
    PVOID FileNode,
    UINT32 FileAttributes, 
    UINT64 CreationTime,
    UINT64 LastAccessTime,
    UINT64 LastWriteTime, 
    FSP_FSCTL_FILE_INFO *FileInfo);  
```

**Parameters**

- _FileSystem_ \- The file system on which this request is posted.
- _Request_ \- The request posted by the kernel mode FSD.
- _FileNode_ \- The file node of the file or directory to set information for.
- _FileAttributes_ \- File attributes to apply to the file or directory. If the value INVALID\_FILE\_ATTRIBUTES
is sent, the file attributes should not be changed.
- _CreationTime_ \- Creation time to apply to the file or directory. If the value 0 is sent, the creation
time should not be changed.
- _LastAccessTime_ \- Last access time to apply to the file or directory. If the value 0 is sent, the last
access time should not be changed.
- _LastWriteTime_ \- Last write time to apply to the file or directory. If the value 0 is sent, the last
write time should not be changed.
- _FileInfo_ \- [out]
Pointer to a structure that will receive the file information on successful return
from this call. This information includes file attributes, file times, etc.

**Return Value**

STATUS\_SUCCESS or error code.


</blockquote>
</details>

<details>
<summary>
<b>SetFileSize</b> - Set file/allocation size.
</summary>
<blockquote>
<br/>

```c
NTSTATUS ( *SetFileSize)(
    FSP_FILE_SYSTEM *FileSystem, 
    FSP_FSCTL_TRANSACT_REQ *Request, 
    PVOID FileNode,
    UINT64 NewSize,
    BOOLEAN SetAllocationSize, 
    FSP_FSCTL_FILE_INFO *FileInfo);  
```

**Parameters**

- _FileSystem_ \- The file system on which this request is posted.
- _Request_ \- The request posted by the kernel mode FSD.
- _FileNode_ \- The file node of the file to set the file/allocation size for.
- _NewSize_ \- New file/allocation size to apply to the file.
- _SetAllocationSize_ \- If TRUE, then the allocation size is being set. if FALSE, then the file size is being set.
- _FileInfo_ \- [out]
Pointer to a structure that will receive the file information on successful return
from this call. This information includes file attributes, file times, etc.

**Return Value**

STATUS\_SUCCESS or error code.

**Discussion**

This function is used to change a file's sizes. Windows file systems maintain two kinds
of sizes: the file size is where the End Of File (EOF) is, and the allocation size is the
actual size that a file takes up on the "disk".

The rules regarding file/allocation size are:

- Allocation size must always be aligned to the allocation unit boundary. The allocation
unit is the product `(UINT64)SectorSize \* (UINT64)SectorsPerAllocationUnit` from
the FSP\_FSCTL\_VOLUME\_PARAMS structure. The FSD will always send properly aligned allocation
sizes when setting the allocation size.


- Allocation size is always greater or equal to the file size.


- A file size of more than the current allocation size will also extend the allocation
size to the next allocation unit boundary.


- An allocation size of less than the current file size should also truncate the current
file size.


</blockquote>
</details>

<details>
<summary>
<b>SetReparsePoint</b> - Set reparse point.
</summary>
<blockquote>
<br/>

```c
NTSTATUS ( *SetReparsePoint)(
    FSP_FILE_SYSTEM *FileSystem, 
    FSP_FSCTL_TRANSACT_REQ *Request, 
    PVOID FileNode, 
    PWSTR FileName,
    PVOID Buffer,
    SIZE_T Size);  
```

**Parameters**

- _FileSystem_ \- The file system on which this request is posted.
- _Request_ \- The request posted by the kernel mode FSD.
- _FileNode_ \- The file node of the reparse point.
- _FileName_ \- The file name of the reparse point.
- _Buffer_ \- Pointer to a buffer that contains the data for this operation.
- _Size_ \- Size of data to write.

**Return Value**

STATUS\_SUCCESS or error code.

**Discussion**

The behavior of this function depends on the value of FSP\_FSCTL\_VOLUME\_PARAMS ::
SymbolicLinksOnly. If the value of SymbolicLinksOnly is FALSE the file system
support full reparse points and this function is expected to set the reparse point
contained in the buffer. If the value of SymbolicLinksOnly is TRUE the file
system supports symbolic links only as reparse points and this function is
expected to set the symbolic link path contained in the buffer.

**See Also**

- GetReparsePoint


</blockquote>
</details>

<details>
<summary>
<b>SetSecurity</b> - Set file or directory security descriptor.
</summary>
<blockquote>
<br/>

```c
NTSTATUS ( *SetSecurity)(
    FSP_FILE_SYSTEM *FileSystem, 
    FSP_FSCTL_TRANSACT_REQ *Request, 
    PVOID FileNode, 
    SECURITY_INFORMATION SecurityInformation,
    PSECURITY_DESCRIPTOR SecurityDescriptor);  
```

**Parameters**

- _FileSystem_ \- The file system on which this request is posted.
- _FileNode_ \- The file node of the file or directory to set the security descriptor for.
- _SecurityInformation_ \- Indicates what part of the file or directory security descriptor to change.
- _SecurityDescriptor_ \- Security descriptor to apply to the file or directory. This security descriptor will
always be in self-relative format.

**Return Value**

STATUS\_SUCCESS or error code.


</blockquote>
</details>

<details>
<summary>
<b>SetVolumeLabel</b> - Set volume label.
</summary>
<blockquote>
<br/>

```c
NTSTATUS ( *SetVolumeLabel)(
    FSP_FILE_SYSTEM *FileSystem, 
    FSP_FSCTL_TRANSACT_REQ *Request, 
    PWSTR VolumeLabel, 
    FSP_FSCTL_VOLUME_INFO *VolumeInfo);  
```

**Parameters**

- _FileSystem_ \- The file system on which this request is posted.
- _Request_ \- The request posted by the kernel mode FSD.
- _VolumeLabel_ \- The new label for the volume.
- _VolumeInfo_ \- [out]
Pointer to a structure that will receive the volume information on successful return
from this call.

**Return Value**

STATUS\_SUCCESS or error code.


</blockquote>
</details>

<details>
<summary>
<b>Write</b> - Write a file.
</summary>
<blockquote>
<br/>

```c
NTSTATUS ( *Write)(
    FSP_FILE_SYSTEM *FileSystem, 
    FSP_FSCTL_TRANSACT_REQ *Request, 
    PVOID FileNode,
    PVOID Buffer,
    UINT64 Offset,
    ULONG Length, 
    BOOLEAN WriteToEndOfFile,
    BOOLEAN ConstrainedIo, 
    PULONG PBytesTransferred,
    FSP_FSCTL_FILE_INFO *FileInfo);  
```

**Parameters**

- _FileSystem_ \- The file system on which this request is posted.
- _Request_ \- The request posted by the kernel mode FSD.
- _FileNode_ \- The file node of the file to be written.
- _Buffer_ \- Pointer to a buffer that contains the data to write.
- _Offset_ \- Offset within the file to write to.
- _Length_ \- Length of data to write.
- _WriteToEndOfFile_ \- When TRUE the file system must write to the current end of file. In this case the Offset
parameter will contain the value -1.
- _ConstrainedIo_ \- When TRUE the file system must not extend the file (i.e. change the file size).
- _PBytesTransferred_ \- [out]
Pointer to a memory location that will receive the actual number of bytes written.
- _FileInfo_ \- [out]
Pointer to a structure that will receive the file information on successful return
from this call. This information includes file attributes, file times, etc.

**Return Value**

STATUS\_SUCCESS or error code. STATUS\_PENDING is supported allowing for asynchronous
operation.


</blockquote>
</details>


</blockquote>
</details>

### Functions

<details>
<summary>
<b>FspFileSystemAddDirInfo</b> - Add directory information to a buffer.
</summary>
<blockquote>
<br/>

```c
FSP_API BOOLEAN FspFileSystemAddDirInfo(
    FSP_FSCTL_DIR_INFO *DirInfo, 
    PVOID Buffer,
    ULONG Length,
    PULONG PBytesTransferred);  
```

**Parameters**

- _DirInfo_ \- The directory information to add. A value of NULL acts as an EOF marker for a ReadDirectory
operation.
- _Buffer_ \- Pointer to a buffer that will receive the results of the read operation. This should contain
the same value passed to the ReadDirectory Buffer parameter.
- _Length_ \- Length of data to read. This should contain the same value passed to the ReadDirectory
Length parameter.
- _PBytesTransferred_ \- [out]
Pointer to a memory location that will receive the actual number of bytes read. This should
contain the same value passed to the ReadDirectory PBytesTransferred parameter.
FspFileSystemAddDirInfo uses the value pointed by this parameter to track how much of the
buffer has been used so far.

**Return Value**

TRUE if the directory information was added, FALSE if there was not enough space to add it.

**Discussion**

This is a helper for implementing the ReadDirectory operation.

**See Also**

- ReadDirectory


</blockquote>
</details>

<details>
<summary>
<b>FspFileSystemCreate</b> - Create a file system object.
</summary>
<blockquote>
<br/>

```c
FSP_API NTSTATUS FspFileSystemCreate(
    PWSTR DevicePath, 
    const FSP_FSCTL_VOLUME_PARAMS *VolumeParams, 
    const FSP_FILE_SYSTEM_INTERFACE *Interface, 
    FSP_FILE_SYSTEM **PFileSystem);  
```

**Parameters**

- _DevicePath_ \- The name of the control device for this file system. This must be either
FSP\_FSCTL\_DISK\_DEVICE\_NAME or FSP\_FSCTL\_NET\_DEVICE\_NAME.
- _VolumeParams_ \- Volume parameters for the newly created file system.
- _Interface_ \- A pointer to the actual operations that actually implement this user mode file system.
- _PFileSystem_ \- [out]
Pointer that will receive the file system object created on successful return from this
call.

**Return Value**

STATUS\_SUCCESS or error code.


</blockquote>
</details>

<details>
<summary>
<b>FspFileSystemDelete</b> - Delete a file system object.
</summary>
<blockquote>
<br/>

```c
FSP_API VOID FspFileSystemDelete(
    FSP_FILE_SYSTEM *FileSystem);  
```

**Parameters**

- _FileSystem_ \- The file system object.


</blockquote>
</details>

<details>
<summary>
<b>FspFileSystemRemoveMountPoint</b> - Remove the mount point for a file system.
</summary>
<blockquote>
<br/>

```c
FSP_API VOID FspFileSystemRemoveMountPoint(
    FSP_FILE_SYSTEM *FileSystem);  
```

**Parameters**

- _FileSystem_ \- The file system object.


</blockquote>
</details>

<details>
<summary>
<b>FspFileSystemSendResponse</b> - Send a response to the FSD.
</summary>
<blockquote>
<br/>

```c
FSP_API VOID FspFileSystemSendResponse(
    FSP_FILE_SYSTEM *FileSystem, 
    FSP_FSCTL_TRANSACT_RSP *Response);  
```

**Parameters**

- _FileSystem_ \- The file system object.
- _Response_ \- The response buffer.

**Discussion**

This call is not required when the user mode file system performs synchronous processing of
requests. It is possible however for the following FSP\_FILE\_SYSTEM\_INTERFACE operations to be
processed asynchronously:

- Read


- Write


- ReadDirectory



These operations are allowed to return STATUS\_PENDING to postpone sending a response to the FSD.
At a later time the file system can use FspFileSystemSendResponse to send the response.


</blockquote>
</details>

<details>
<summary>
<b>FspFileSystemSetMountPoint</b> - Set the mount point for a file system.
</summary>
<blockquote>
<br/>

```c
FSP_API NTSTATUS FspFileSystemSetMountPoint(
    FSP_FILE_SYSTEM *FileSystem,
    PWSTR MountPoint);  
```

**Parameters**

- _FileSystem_ \- The file system object.
- _MountPoint_ \- The mount point for the new file system. A value of NULL means that the file system should
use the next available drive letter counting downwards from Z: as its mount point.

**Return Value**

STATUS\_SUCCESS or error code.

**Discussion**

This function currently only supports drive letters (X:) as mount points. Refer to the
documentation of the DefineDosDevice Windows API to better understand how drive letters are
created.


</blockquote>
</details>

<details>
<summary>
<b>FspFileSystemSetOperationGuardStrategy</b> - Set file system locking strategy.
</summary>
<blockquote>
<br/>

```c
static inline VOID FspFileSystemSetOperationGuardStrategy(
    FSP_FILE_SYSTEM *FileSystem, 
    FSP_FILE_SYSTEM_OPERATION_GUARD_STRATEGY GuardStrategy) 
```

**Parameters**

- _FileSystem_ \- The file system object.
- _GuardStrategy_ \- The locking (guard) strategy.

**See Also**

- FSP\_FILE\_SYSTEM\_OPERATION\_GUARD\_STRATEGY


</blockquote>
</details>

<details>
<summary>
<b>FspFileSystemStartDispatcher</b> - Start the file system dispatcher.
</summary>
<blockquote>
<br/>

```c
FSP_API NTSTATUS FspFileSystemStartDispatcher(
    FSP_FILE_SYSTEM *FileSystem,
    ULONG ThreadCount);  
```

**Parameters**

- _FileSystem_ \- The file system object.
- _ThreadCount_ \- The number of threads for the file system dispatcher. A value of 0 will create a default
number of threads and should be chosen in most cases.

**Return Value**

STATUS\_SUCCESS or error code.

**Discussion**

The file system dispatcher is used to dispatch operations posted by the FSD to the user mode
file system. Once this call starts executing the user mode file system will start receiving
file system requests from the kernel.


</blockquote>
</details>

<details>
<summary>
<b>FspFileSystemStopDispatcher</b> - Stop the file system dispatcher.
</summary>
<blockquote>
<br/>

```c
FSP_API VOID FspFileSystemStopDispatcher(
    FSP_FILE_SYSTEM *FileSystem);  
```

**Parameters**

- _FileSystem_ \- The file system object.


</blockquote>
</details>

### Typedefs

<details>
<summary>
<b>FSP_FILE_SYSTEM_OPERATION_GUARD_STRATEGY</b> - User mode file system locking strategy.
</summary>
<blockquote>
<br/>

```c
typedef enum { 
    FSP_FILE_SYSTEM_OPERATION_GUARD_STRATEGY_FINE = 0, 
    FSP_FILE_SYSTEM_OPERATION_GUARD_STRATEGY_COARSE, 
} FSP_FILE_SYSTEM_OPERATION_GUARD_STRATEGY;  
```

**Discussion**

Two concurrency models are provided:

1. A fine-grained concurrency model where file system NAMESPACE accesses
are guarded using an exclusive-shared (read-write) lock. File I/O is not
guarded and concurrent reads/writes/etc. are possible. [Note that the FSD
will still apply an exclusive-shared lock PER INDIVIDUAL FILE, but it will
not limit I/O operations for different files.]
The fine-grained concurrency model applies the exclusive-shared lock as
follows:

- EXCL: SetVolumeLabel, Create, Cleanup(Delete), SetInformation(Rename)


- SHRD: GetVolumeInfo, Open, SetInformation(Disposition), ReadDirectory


- NONE: all other operations



2. A coarse-grained concurrency model where all file system accesses are
guarded by a mutually exclusive lock.

**See Also**

- FspFileSystemSetOperationGuardStrategy


</blockquote>
</details>

## SERVICE FRAMEWORK

User mode file systems typically are run as Windows services. WinFsp provides an API to make
the creation of Windows services easier. This API is provided for convenience and is not
necessary to expose a user mode file system to Windows.

### Functions

<details>
<summary>
<b>FspServiceAcceptControl</b> - Configure the control codes that a service accepts.
</summary>
<blockquote>
<br/>

```c
FSP_API VOID FspServiceAcceptControl(
    FSP_SERVICE *Service,
    ULONG Control);  
```

**Parameters**

- _Service_ \- The service object.
- _Control_ \- The control codes to accept. Note that the SERVICE\_ACCEPT\_PAUSE\_CONTINUE code is silently
ignored.

**Discussion**

This API should be used prior to Start operations.


</blockquote>
</details>

<details>
<summary>
<b>FspServiceAllowConsoleMode</b> - Allow a service to run in console mode.
</summary>
<blockquote>
<br/>

```c
FSP_API VOID FspServiceAllowConsoleMode(
    FSP_SERVICE *Service);  
```

**Parameters**

- _Service_ \- The service object.

**Discussion**

A service that is run in console mode runs with a console attached and outside the control of
the Service Control Manager. This is useful for debugging and testing a service during
development.

User mode file systems that wish to use the WinFsp Launcher functionality must also use this
call. The WinFsp Launcher is a Windows service that can be configured to launch and manage
multiple instances of a user mode file system.


</blockquote>
</details>

<details>
<summary>
<b>FspServiceCreate</b> - Create a service object.
</summary>
<blockquote>
<br/>

```c
FSP_API NTSTATUS FspServiceCreate(
    PWSTR ServiceName, 
    FSP_SERVICE_START *OnStart, 
    FSP_SERVICE_STOP *OnStop, 
    FSP_SERVICE_CONTROL *OnControl, 
    FSP_SERVICE **PService);  
```

**Parameters**

- _ServiceName_ \- The name of the service.
- _OnStart_ \- Function to call when the service starts.
- _OnStop_ \- Function to call when the service stops.
- _OnControl_ \- Function to call when the service receives a service control code.
- _PService_ \- [out]
Pointer that will receive the service object created on successful return from this
call.

**Return Value**

STATUS\_SUCCESS or error code.


</blockquote>
</details>

<details>
<summary>
<b>FspServiceDelete</b> - Delete a service object.
</summary>
<blockquote>
<br/>

```c
FSP_API VOID FspServiceDelete(
    FSP_SERVICE *Service);  
```

**Parameters**

- _Service_ \- The service object.


</blockquote>
</details>

<details>
<summary>
<b>FspServiceGetExitCode</b> - Get the service process exit code.
</summary>
<blockquote>
<br/>

```c
FSP_API ULONG FspServiceGetExitCode(
    FSP_SERVICE *Service);  
```

**Parameters**

- _Service_ \- The service object.

**Return Value**

Service process exit code.


</blockquote>
</details>

<details>
<summary>
<b>FspServiceIsInteractive</b> - Determine if the current process is running in user interactive mode.
</summary>
<blockquote>
<br/>

```c
FSP_API BOOLEAN FspServiceIsInteractive(
    VOID);  
```

**Return Value**

TRUE if the process is running in running user interactive mode.


</blockquote>
</details>

<details>
<summary>
<b>FspServiceLog</b> - Log a service message.
</summary>
<blockquote>
<br/>

```c
FSP_API VOID FspServiceLog(
    ULONG Type,
    PWSTR Format,
    ...);  
```

**Parameters**

- _Type_ \- One of EVENTLOG\_INFORMATION\_TYPE, EVENTLOG\_WARNING\_TYPE, EVENTLOG\_ERROR\_TYPE.
- _Format_ \- Format specification. This function uses the Windows wsprintf API for formatting. Refer to
that API's documentation for details on the format specification.

**Discussion**

This function can be used to log an arbitrary message to the Windows Event Log or to the current
console if running in user interactive mode.


</blockquote>
</details>

<details>
<summary>
<b>FspServiceLoop</b> - Run a service main loop.
</summary>
<blockquote>
<br/>

```c
FSP_API NTSTATUS FspServiceLoop(
    FSP_SERVICE *Service);  
```

**Parameters**

- _Service_ \- The service object.

**Return Value**

STATUS\_SUCCESS or error code.

**Discussion**

This function starts and runs a service. It executes the Windows StartServiceCtrlDispatcher API
to connect the service process to the Service Control Manager. If the Service Control Manager is
not available (and console mode is allowed) it will enter console mode.


</blockquote>
</details>

<details>
<summary>
<b>FspServiceRequestTime</b> - Request additional time from the Service Control Manager.
</summary>
<blockquote>
<br/>

```c
FSP_API VOID FspServiceRequestTime(
    FSP_SERVICE *Service,
    ULONG Time);  
```

**Parameters**

- _Service_ \- The service object.
- _Time_ \- Additional time (in milliseconds).

**Discussion**

This API should be used during Start and Stop operations only.


</blockquote>
</details>

<details>
<summary>
<b>FspServiceRunEx</b> - Run a service.
</summary>
<blockquote>
<br/>

```c
FSP_API ULONG FspServiceRunEx(
    PWSTR ServiceName, 
    FSP_SERVICE_START *OnStart, 
    FSP_SERVICE_STOP *OnStop, 
    FSP_SERVICE_CONTROL *OnControl, 
    PVOID UserContext);  
```

**Parameters**

- _ServiceName_ \- The name of the service.
- _OnStart_ \- Function to call when the service starts.
- _OnStop_ \- Function to call when the service stops.
- _OnControl_ \- Function to call when the service receives a service control code.

**Return Value**

Service process exit code.

**Discussion**

This function wraps calls to FspServiceCreate, FspServiceLoop and FspServiceDelete to create,
run and delete a service. It is intended to be used from a service's main/wmain function.

This function runs a service with console mode allowed.


</blockquote>
</details>

<details>
<summary>
<b>FspServiceSetExitCode</b> - Set the service process exit code.
</summary>
<blockquote>
<br/>

```c
FSP_API VOID FspServiceSetExitCode(
    FSP_SERVICE *Service,
    ULONG ExitCode);  
```

**Parameters**

- _Service_ \- The service object.
- _ExitCode_ \- Service process exit code.


</blockquote>
</details>

<details>
<summary>
<b>FspServiceStop</b> - Stops a running service.
</summary>
<blockquote>
<br/>

```c
FSP_API VOID FspServiceStop(
    FSP_SERVICE *Service);  
```

**Parameters**

- _Service_ \- The service object.

**Return Value**

STATUS\_SUCCESS or error code.

**Discussion**

Stopping a service usually happens when the Service Control Manager instructs the service to
stop. In some situations (e.g. fatal errors) the service may wish to stop itself. It can do so
in a clean manner by calling this function.


</blockquote>
</details>


<br/>
<p align="center">
<sub>
Copyright © 2015-2016 Bill Zissimopoulos
&nbsp;|&nbsp;
Updated: 2016-07-22
<br/>
Generated with <a href="https://github.com/billziss-gh/prettydoc">prettydoc</a>
</sub>
</p>
