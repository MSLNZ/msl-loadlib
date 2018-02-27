#include "extcode.h"
#pragma pack(push)
#pragma pack(1)

#ifdef __cplusplus
extern "C" {
#endif
typedef uint16_t  Enum;
#define Enum_Sample 0
#define Enum_Population 1

/*!
 * stdev
 */
void __cdecl stdev(double X[], int32_t lenX, Enum WeightingSample, 
	double *mean, double *variance, double *standardDeviation);

MgErr __cdecl LVDLLStatus(char *errStr, int errStrLen, void *module);

#ifdef __cplusplus
} // extern "C"
#endif

#pragma pack(pop)

